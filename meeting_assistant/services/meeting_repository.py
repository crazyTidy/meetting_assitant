"""Meeting repository for data access."""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from ..models.meeting_model import Meeting, MeetingStatus, ProcessingStage
from ..models.participant_model import Participant
from ..models.summary_model import Summary
from ..models.speaker_segment_model import SpeakerSegment
from ..models.user_model import User


class MeetingRepository:
    """Repository for meeting data operations."""

    async def create(
        self,
        db: AsyncSession,
        title: str,
        audio_path: str,
        duration: Optional[int] = None,
        creator_id: Optional[str] = None
    ) -> Meeting:
        """Create a new meeting."""
        meeting = Meeting(
            title=title,
            audio_path=audio_path,
            status=MeetingStatus.PENDING,
            duration=duration,
            creator_id=creator_id
        )
        db.add(meeting)
        await db.flush()
        await db.refresh(meeting)
        return meeting

    async def get(
        self,
        db: AsyncSession,
        meeting_id: str
    ) -> Optional[Meeting]:
        """Get meeting by ID."""
        result = await db.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        )
        return result.scalars().first()

    async def get_with_details(
        self,
        db: AsyncSession,
        meeting_id: str
    ) -> Optional[Meeting]:
        """Get meeting with participants, speaker segments, merged segments, and summary."""
        result = await db.execute(
            select(Meeting)
            .options(
                selectinload(Meeting.creator),
                selectinload(Meeting.participants),
                selectinload(Meeting.speaker_segments),
                selectinload(Meeting.merged_segments),
                selectinload(Meeting.summary)
            )
            .where(Meeting.id == meeting_id)
        )
        return result.scalars().first()

    async def get_list(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 10,
        creator_id: Optional[str] = None
    ) -> Tuple[List[Meeting], int]:
        """Get paginated list of meetings."""
        query = select(Meeting)

        # Search filter
        if search:
            query = query.where(
                Meeting.title.ilike(f"%{search}%")
            )

        # Filter by creator
        if creator_id:
            query = query.where(Meeting.creator_id == creator_id)

        # Count total
        count_query = select(func.count()).select_from(
            query.subquery()
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Order and paginate
        query = query.order_by(Meeting.created_at.desc())
        query = query.offset((page - 1) * size).limit(size)

        result = await db.execute(query)
        meetings = result.scalars().all()

        return list(meetings), total

    async def update_status(
        self,
        db: AsyncSession,
        meeting_id: str,
        status: MeetingStatus,
        progress: int = 0,
        error_message: Optional[str] = None
    ) -> Optional[Meeting]:
        """Update meeting status."""
        meeting = await self.get(db, meeting_id)
        if meeting:
            meeting.status = status
            meeting.progress = progress
            if error_message:
                meeting.error_message = error_message
            await db.flush()
            await db.refresh(meeting)
        return meeting

    async def update_stage(
        self,
        db: AsyncSession,
        meeting_id: str,
        status: MeetingStatus,
        stage: ProcessingStage,
        progress: int = 0,
        error_message: Optional[str] = None
    ) -> Optional[Meeting]:
        """Update meeting status with stage information."""
        meeting = await self.get(db, meeting_id)
        if meeting:
            meeting.status = status
            meeting.stage = stage
            meeting.progress = progress
            if error_message:
                meeting.error_message = error_message
            await db.flush()
            await db.refresh(meeting)
        return meeting

    async def update_duration(
        self,
        db: AsyncSession,
        meeting_id: str,
        duration: int
    ) -> Optional[Meeting]:
        """Update meeting duration."""
        meeting = await self.get(db, meeting_id)
        if meeting:
            meeting.duration = duration
            await db.flush()
            await db.refresh(meeting)
        return meeting

    async def delete(
        self,
        db: AsyncSession,
        meeting_id: str
    ) -> bool:
        """Delete meeting."""
        meeting = await self.get(db, meeting_id)
        if meeting:
            await db.delete(meeting)
            return True
        return False


class ParticipantRepository:
    """Repository for participant data operations."""

    async def create(
        self,
        db: AsyncSession,
        meeting_id: str,
        speaker_id: str,
        display_name: str,
        voice_segment_path: Optional[str] = None
    ) -> Participant:
        """Create a new participant."""
        participant = Participant(
            meeting_id=meeting_id,
            speaker_id=speaker_id,
            display_name=display_name,
            voice_segment_path=voice_segment_path
        )
        db.add(participant)
        await db.flush()
        await db.refresh(participant)
        return participant

    async def get(
        self,
        db: AsyncSession,
        participant_id: str
    ) -> Optional[Participant]:
        """Get participant by ID."""
        result = await db.execute(
            select(Participant).where(Participant.id == participant_id)
        )
        return result.scalars().first()

    async def get_by_meeting(
        self,
        db: AsyncSession,
        meeting_id: str
    ) -> List[Participant]:
        """Get all participants for a meeting."""
        result = await db.execute(
            select(Participant)
            .where(Participant.meeting_id == meeting_id)
            .order_by(Participant.speaker_id)
        )
        return list(result.scalars().all())

    async def update_name(
        self,
        db: AsyncSession,
        participant_id: str,
        display_name: str
    ) -> Optional[Participant]:
        """Update participant display name."""
        participant = await self.get(db, participant_id)
        if participant:
            participant.display_name = display_name
            await db.flush()
            await db.refresh(participant)
        return participant


class SummaryRepository:
    """Repository for summary data operations."""

    async def create(
        self,
        db: AsyncSession,
        meeting_id: str,
        content: str,
        raw_response: Optional[str] = None
    ) -> Summary:
        """Create a new summary."""
        summary = Summary(
            meeting_id=meeting_id,
            content=content,
            raw_response=raw_response
        )
        db.add(summary)
        await db.flush()
        await db.refresh(summary)
        return summary

    async def get_by_meeting(
        self,
        db: AsyncSession,
        meeting_id: str
    ) -> Optional[Summary]:
        """Get summary by meeting ID."""
        result = await db.execute(
            select(Summary).where(Summary.meeting_id == meeting_id)
        )
        return result.scalars().first()

    async def update(
        self,
        db: AsyncSession,
        meeting_id: str,
        content: str
    ) -> Optional[Summary]:
        """Update summary content."""
        summary = await self.get_by_meeting(db, meeting_id)
        if summary:
            summary.content = content
            await db.flush()
            await db.refresh(summary)
        return summary


# Singleton instances
meeting_repository = MeetingRepository()
participant_repository = ParticipantRepository()
summary_repository = SummaryRepository()
