"""Meeting service for business logic."""
import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, Tuple, List
from fastapi import UploadFile, BackgroundTasks

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from ..settings.config import settings
from ..models.meeting_model import Meeting, MeetingStatus, ProcessingStage
from ..models.speaker_segment_model import SpeakerSegment
from ..models.merged_segment_model import MergedSegment
from ..models.summary_model import Summary
from .meeting_repository import (
    meeting_repository,
    participant_repository,
    summary_repository
)
from ..items.meeting_item import MeetingListResponse, MeetingStatusResponse
from .processor import process_meeting_task
from .regenerator import regenerate_summary_task
from ..utils.audio_util import get_audio_duration
from ..utils.storage_util import storage_service


class MeetingService:
    """Business logic for meetings."""

    def __init__(self):
        self.repository = meeting_repository

    def _get_status_message(self, status: MeetingStatus, progress: int, stage: Optional[ProcessingStage] = None) -> str:
        """Get human-readable status message."""
        if status == MeetingStatus.PENDING:
            return "等待处理..."
        elif status == MeetingStatus.COMPLETED:
            return "处理完成"
        elif status == MeetingStatus.FAILED:
            if stage == ProcessingStage.SEPARATION_COMPLETED:
                return f"部分完成 (人声分离完成 {progress}%, 总结生成失败)"
            return "处理失败"
        elif status == MeetingStatus.PROCESSING:
            # 根据阶段返回不同的消息
            stage_messages = {
                ProcessingStage.INITIALIZING: f"初始化中... ({progress}%)",
                ProcessingStage.SEPARATING: f"人声分离中... ({progress}%)",
                ProcessingStage.SEPARATION_COMPLETED: f"人声分离完成 ✅ ({progress}%)",
                ProcessingStage.SUMMARIZING: f"AI 总结生成中... ({progress}%)",
                ProcessingStage.COMPLETED: f"处理完成 ✅ ({progress}%)",
            }
            return stage_messages.get(stage, f"正在处理... ({progress}%)")
        return "未知状态"

    def _get_stage_description(self, stage: Optional[ProcessingStage]) -> Optional[str]:
        """Get human-readable stage description."""
        if not stage:
            return None
        descriptions = {
            ProcessingStage.INITIALIZING: "初始化处理",
            ProcessingStage.SEPARATING: "人声分离进行中",
            ProcessingStage.SEPARATION_COMPLETED: "人声分离完成",
            ProcessingStage.SUMMARIZING: "AI 总结生成中",
            ProcessingStage.COMPLETED: "全部完成",
        }
        return descriptions.get(stage)

    async def create_meeting(
        self,
        db: AsyncSession,
        title: str,
        audio_file: UploadFile,
        background_tasks: BackgroundTasks,
        creator_id: Optional[str] = None
    ) -> Meeting:
        """Create a meeting and start processing."""
        # Validate file extension
        file_ext = Path(audio_file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_AUDIO_EXTENSIONS:
            raise ValueError(
                f"不支持的音频格式。支持的格式: {', '.join(settings.ALLOWED_AUDIO_EXTENSIONS)}"
            )

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # Read and validate file
        content = await audio_file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise ValueError(
                f"文件过大。最大允许: {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB"
            )

        # Save file to storage (local or MinIO)
        storage_path = await storage_service.save_file(content, unique_filename)

        # Get actual file path for duration check
        actual_path = await storage_service.get_file_path(storage_path)
        duration = await get_audio_duration(actual_path)

        # Create meeting record
        meeting = await self.repository.create(
            db=db,
            title=title,
            audio_path=storage_path,
            duration=duration,
            creator_id=creator_id
        )

        # Commit immediately so background task can find the meeting
        await db.commit()
        await db.refresh(meeting)

        # Start background processing
        background_tasks.add_task(
            process_meeting_task,
            meeting_id=meeting.id
        )

        return meeting

    async def get_meeting(
        self,
        db: AsyncSession,
        meeting_id: str
    ) -> Optional[Meeting]:
        """Get meeting with details."""
        return await self.repository.get_with_details(db, meeting_id)

    async def get_meeting_list(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        creator_id: Optional[str] = None
    ) -> MeetingListResponse:
        """Get paginated meeting list."""
        meetings, total = await self.repository.get_list(
            db=db,
            search=search,
            page=page,
            size=size,
            creator_id=creator_id
        )

        pages = (total + size - 1) // size if total > 0 else 0

        return MeetingListResponse(
            items=meetings,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    async def get_meeting_status(
        self,
        db: AsyncSession,
        meeting_id: str
    ) -> Optional[MeetingStatusResponse]:
        """Get meeting processing status."""
        meeting = await self.repository.get(db, meeting_id)
        if not meeting:
            return None

        return MeetingStatusResponse(
            id=meeting.id,
            status=meeting.status,
            progress=meeting.progress,
            stage=meeting.stage,
            message=self._get_status_message(meeting.status, meeting.progress, meeting.stage),
            stage_description=self._get_stage_description(meeting.stage)
        )

    async def delete_meeting(
        self,
        db: AsyncSession,
        meeting_id: str
    ) -> bool:
        """Delete meeting and associated files."""
        meeting = await self.repository.get(db, meeting_id)
        if not meeting:
            return False

        # Delete audio file
        try:
            if os.path.exists(meeting.audio_path):
                os.remove(meeting.audio_path)
        except Exception:
            pass  # Ignore file deletion errors

        # Delete from database
        return await self.repository.delete(db, meeting_id)


class SummaryService:
    """Business logic for summaries."""

    def __init__(self):
        self.repository = summary_repository

    async def update_summary(
        self,
        db: AsyncSession,
        meeting_id: str,
        content: str
    ) -> Optional[dict]:
        """Update summary content."""
        updated = await self.repository.update(
            db=db,
            meeting_id=meeting_id,
            content=content
        )

        if updated:
            return {
                "id": updated.id,
                "content": updated.content,
                "generated_at": updated.generated_at.isoformat()
            }
        return None


class ParticipantService:
    """Business logic for participants."""

    def __init__(self):
        self.repository = participant_repository

    async def update_participant_name(
        self,
        db: AsyncSession,
        meeting_id: str,
        participant_id: str,
        display_name: str
    ) -> Optional[dict]:
        """Update participant display name."""
        # Verify participant belongs to meeting
        participant = await self.repository.get(db, participant_id)
        if not participant or participant.meeting_id != meeting_id:
            return None

        updated = await self.repository.update_name(
            db=db,
            participant_id=participant_id,
            display_name=display_name
        )

        if updated:
            return {
                "id": updated.id,
                "speaker_id": updated.speaker_id,
                "display_name": updated.display_name
            }
        return None

    async def update_participant_name_by_speaker_id(
        self,
        db: AsyncSession,
        speaker_id: str,
        display_name: str
    ) -> Optional[int]:
        """
        Update display name for all participants with the given speaker_id.

        This updates all participants (across all meetings) that have the given speaker_id.

        Args:
            db: Database session
            speaker_id: Speaker identifier (e.g., "speaker_1")
            display_name: New display name

        Returns:
            Number of participants updated, or None if speaker_id not found
        """
        from sqlalchemy import select, update
        from ..models.participant_model import Participant

        # First check if any participants exist with this speaker_id
        result = await db.execute(
            select(Participant).where(Participant.speaker_id == speaker_id)
        )
        participants = result.scalars().all()

        if not participants:
            return None

        # Update all participants with this speaker_id
        await db.execute(
            update(Participant)
            .where(Participant.speaker_id == speaker_id)
            .values(display_name=display_name)
        )

        await db.commit()

        return len(participants)


class RegenerateService:
    """Business logic for regenerating summaries."""

    def __init__(self):
        self.repository = meeting_repository

    async def regenerate_summary(
        self,
        db: AsyncSession,
        meeting_id: str,
        background_tasks: BackgroundTasks
    ) -> Optional[MeetingStatusResponse]:
        """
        Regenerate meeting summary using existing speaker segments.

        This validates that the meeting has the required data (merged segments)
        and triggers a background task to regenerate the summary.

        Args:
            db: Database session
            meeting_id: Meeting UUID
            background_tasks: FastAPI background tasks

        Returns:
            MeetingStatusResponse with processing status, or None if meeting not found
        """
        # Get meeting with details
        meeting = await meeting_repository.get_with_details(db, meeting_id)
        if not meeting:
            return None

        # Check if meeting has merged segments (required for regeneration)
        if not meeting.merged_segments or len(meeting.merged_segments) == 0:
            raise ValueError("会议没有发言记录数据，无法重新生成纪要")

        # Check if meeting is currently being processed
        if meeting.status == MeetingStatus.PROCESSING or meeting.status == MeetingStatus.PENDING:
            raise ValueError("会议正在处理中，请等待处理完成后再重新生成")

        # Update meeting status to processing
        await meeting_repository.update_stage(
            db=db,
            meeting_id=meeting_id,
            status=MeetingStatus.PROCESSING,
            stage=ProcessingStage.SUMMARIZING,
            progress=50,
            error_message=None  # Clear any previous error
        )
        await db.commit()

        # Start background regeneration task
        background_tasks.add_task(
            regenerate_summary_task,
            meeting_id=meeting_id
        )

        return MeetingStatusResponse(
            id=meeting.id,
            status=MeetingStatus.PROCESSING,
            progress=50,
            stage=ProcessingStage.SUMMARIZING,
            message="正在重新生成会议纪要...",
            stage_description="AI 总结生成中"
        )


# Singleton instances
meeting_service = MeetingService()
summary_service = SummaryService()
participant_service = ParticipantService()
regenerate_service = RegenerateService()
