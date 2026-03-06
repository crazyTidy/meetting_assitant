"""Background task for regenerating meeting summaries."""
import logging
from typing import List

from ..settings.database import AsyncSessionLocal
from ..models.meeting_model import MeetingStatus, ProcessingStage
from .meeting_repository import (
    meeting_repository,
    summary_repository
)
from .separation_service import SpeakerInfo, SpeakerSegment
from .llm_service import llm_service

logger = logging.getLogger(__name__)


async def regenerate_summary_task(meeting_id: str):
    """
    Background task to regenerate meeting summary using existing merged segments.

    This task:
    1. Fetches the meeting with merged segments from database
    2. Uses LLM service to generate a new summary
    3. Updates or creates the summary record
    4. Updates meeting status to COMPLETED

    Args:
        meeting_id: Meeting UUID
    """
    logger.info(f"[REGENERATE] Starting summary regeneration for meeting: {meeting_id}")

    async with AsyncSessionLocal() as db:
        try:
            # Get meeting with details
            logger.info(f"[REGENERATE][{meeting_id}] Fetching meeting from database...")
            meeting = await meeting_repository.get_with_details(db, meeting_id)
            if not meeting:
                logger.error(f"[REGENERATE][{meeting_id}] Meeting not found")
                return

            logger.info(f"[REGENERATE][{meeting_id}] Meeting found: {meeting.title}")

            # Check if merged segments exist
            if not meeting.merged_segments or len(meeting.merged_segments) == 0:
                logger.error(f"[REGENERATE][{meeting_id}] No merged segments found")
                await meeting_repository.update_stage(
                    db=db,
                    meeting_id=meeting_id,
                    status=MeetingStatus.FAILED,
                    stage=ProcessingStage.SUMMARIZING,
                    progress=50,
                    error_message="无法重新生成：会议没有发言记录数据"
                )
                await db.commit()
                return

            logger.info(f"[REGENERATE][{meeting_id}] Found {len(meeting.merged_segments)} merged segments")

            # Update progress
            await meeting_repository.update_stage(
                db=db,
                meeting_id=meeting_id,
                status=MeetingStatus.PROCESSING,
                stage=ProcessingStage.SUMMARIZING,
                progress=60
            )
            await db.commit()

            logger.info(
                f"[REGENERATE][{meeting_id}] Processing {len(meeting.participants)} participants"
            )

            # Build old speaker name map (default display names)
            # Default format is "说话人 1", "说话人 2", etc.
            old_name_map = {}
            for participant in meeting.participants:
                if participant.speaker_id.startswith("speaker_"):
                    try:
                        speaker_num = participant.speaker_id.split('_')[1]
                        old_name_map[participant.speaker_id] = f"说话人 {speaker_num}"
                    except (IndexError, ValueError):
                        # If speaker_id format is unexpected, skip
                        pass

            logger.info(
                f"[REGENERATE][{meeting_id}] Old name map: {old_name_map}"
            )

            # Build speaker info from participants
            speakers: List[SpeakerInfo] = []
            speaker_name_map = {}

            for participant in meeting.participants:
                # Calculate total speaking duration from merged segments
                total_duration = sum(
                    seg.duration for seg in meeting.merged_segments
                    if seg.speaker_id == participant.speaker_id
                )

                # Get old and new names for this speaker
                new_name = participant.display_name
                old_name = old_name_map.get(participant.speaker_id, "")

                # Build segments list for this speaker with name replacement
                speaker_segments = []
                for seg in meeting.merged_segments:
                    if seg.speaker_id == participant.speaker_id:
                        # Apply name replacement to transcript
                        transcript = seg.transcript or ""
                        if old_name and new_name and old_name != new_name:
                            transcript = transcript.replace(old_name, new_name)

                        speaker_segments.append(
                            SpeakerSegment(
                                speaker_id=seg.speaker_id,
                                start_time=seg.start_time,
                                end_time=seg.end_time,
                                transcript=transcript
                            )
                        )

                speakers.append(SpeakerInfo(
                    speaker_id=participant.speaker_id,
                    display_name=participant.display_name,
                    segments=speaker_segments,
                    total_duration=total_duration
                ))
                speaker_name_map[participant.speaker_id] = participant.display_name

            logger.info(
                f"[REGENERATE][{meeting_id}] Built speaker info: {len(speakers)} speakers"
            )

            # Build timeline from merged segments for LLM
            # Apply name replacement to transcripts (same logic as in speakers above)
            timeline_for_llm: List[SpeakerSegment] = []
            for merged_seg in meeting.merged_segments:
                # Get transcript and replace old name with new name
                transcript = merged_seg.transcript or ""
                old_name = old_name_map.get(merged_seg.speaker_id, "")
                new_name = speaker_name_map.get(merged_seg.speaker_id, "")

                # Replace old name with new name in transcript
                if old_name and new_name and old_name != new_name:
                    transcript = transcript.replace(old_name, new_name)

                timeline_for_llm.append(
                    SpeakerSegment(
                        speaker_id=merged_seg.speaker_id,
                        start_time=merged_seg.start_time,
                        end_time=merged_seg.end_time,
                        transcript=transcript
                    )
                )

            logger.info(
                f"[REGENERATE][{meeting_id}] Built timeline with {len(timeline_for_llm)} segments"
            )

            # Update progress
            await meeting_repository.update_stage(
                db=db,
                meeting_id=meeting_id,
                status=MeetingStatus.PROCESSING,
                stage=ProcessingStage.SUMMARIZING,
                progress=70
            )
            await db.commit()

            # Generate new summary using LLM
            logger.info(f"[REGENERATE][{meeting_id}] Generating new summary with LLM...")
            summary_result = await llm_service.generate_summary_from_timeline(
                audio_path=meeting.audio_path,
                speakers=speakers,
                meeting_title=meeting.title,
                timeline=timeline_for_llm,
                speaker_name_map=speaker_name_map
            )

            logger.info(
                f"[REGENERATE][{meeting_id}] Summary generated: "
                f"{len(summary_result.content)} chars"
            )

            # Update progress
            await meeting_repository.update_stage(
                db=db,
                meeting_id=meeting_id,
                status=MeetingStatus.PROCESSING,
                stage=ProcessingStage.SUMMARIZING,
                progress=90
            )
            await db.commit()

            # Update or create summary
            existing_summary = await summary_repository.get_by_meeting(db, meeting_id)
            if existing_summary:
                # Update existing summary
                existing_summary.content = summary_result.content
                existing_summary.raw_response = summary_result.raw_response
                logger.info(f"[REGENERATE][{meeting_id}] Updated existing summary")
            else:
                # Create new summary
                await summary_repository.create(
                    db=db,
                    meeting_id=meeting_id,
                    content=summary_result.content,
                    raw_response=summary_result.raw_response
                )
                logger.info(f"[REGENERATE][{meeting_id}] Created new summary")

            await db.commit()

            # Mark as completed
            await meeting_repository.update_stage(
                db=db,
                meeting_id=meeting_id,
                status=MeetingStatus.COMPLETED,
                stage=ProcessingStage.COMPLETED,
                progress=100,
                error_message=None  # Clear any previous error
            )
            await db.commit()

            logger.info(f"[REGENERATE][{meeting_id}] Summary regeneration completed successfully")

        except Exception as e:
            logger.exception(f"[REGENERATE][{meeting_id}] Error during regeneration: {e}")

            # Mark as failed
            async with AsyncSessionLocal() as error_db:
                await meeting_repository.update_stage(
                    db=error_db,
                    meeting_id=meeting_id,
                    status=MeetingStatus.FAILED,
                    stage=ProcessingStage.SEPARATION_COMPLETED,
                    progress=50,
                    error_message=f"重新生成失败: {str(e)}"
                )
                await error_db.commit()

            logger.error(f"[REGENERATE][{meeting_id}] Regeneration FAILED")
