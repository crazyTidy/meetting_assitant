"""Background task processor for meeting processing."""
import asyncio
import logging
from typing import Optional, List, Tuple

from ..settings.database import AsyncSessionLocal
from ..models.meeting_model import MeetingStatus, ProcessingStage
from .meeting_repository import (
    meeting_repository,
    participant_repository,
    summary_repository
)
from ..models.speaker_segment_model import SpeakerSegment
from ..models.merged_segment_model import MergedSegment
from .separation_service import separation_service
from .llm_service import llm_service

logger = logging.getLogger(__name__)

# Gap threshold for splitting segments (in seconds)
# 同一说话人的间隔超过此阈值则分开展示
SEGMENT_GAP_THRESHOLD = 1.0


def _log_separator(title: str = ""):
    """Log a visual separator for better log readability."""
    separator = "=" * 80
    if title:
        logger.info(f"{separator} {title} {separator}")
    else:
        logger.info(separator)


def _get_stage_description(stage: ProcessingStage) -> str:
    """Get human-readable stage description."""
    descriptions = {
        ProcessingStage.INITIALIZING: "初始化中...",
        ProcessingStage.SEPARATING: "人声分离中... (10-50%)",
        ProcessingStage.SEPARATION_COMPLETED: "人声分离完成 ✅",
        ProcessingStage.SUMMARIZING: "AI 总结生成中... (50-100%)",
        ProcessingStage.COMPLETED: "处理完成 ✅",
    }
    return descriptions.get(stage, "处理中...")


def _merge_consecutive_segments(timeline: List) -> List[dict]:
    """
    Merge consecutive segments from the same speaker.

    Rules:
    1. Merge consecutive segments from the same speaker
    2. Split if gap between segments is > SEGMENT_GAP_THRESHOLD (1 second)
    3. Continue merging until different speaker speaks

    Args:
        timeline: List of SpeakerSegment objects sorted by start_time

    Returns:
        List of merged segment dictionaries with keys:
        - speaker_id: Speaker identifier
        - start_time: Start time in seconds
        - end_time: End time in seconds
        - duration: Duration in seconds
        - transcript: Combined transcript text
        - segment_count: Number of original segments merged
    """
    if not timeline:
        return []

    merged = []
    current_seg = None

    for segment in timeline:
        segment_speaker = segment.speaker_id
        segment_start = segment.start_time
        segment_end = segment.end_time
        segment_transcript = segment.transcript

        # Check if we should merge with current segment
        if current_seg is None:
            # First segment - start new merged segment
            current_seg = {
                'speaker_id': segment_speaker,
                'start_time': segment_start,
                'end_time': segment_end,
                'duration': segment_end - segment_start,
                'transcript': segment_transcript or '',
                'segment_count': 1
            }
        elif current_seg['speaker_id'] == segment_speaker:
            # Same speaker - check if gap is small enough to merge
            gap = segment_start - current_seg['end_time']

            if gap <= SEGMENT_GAP_THRESHOLD:
                # Merge with current segment
                current_seg['end_time'] = segment_end
                current_seg['duration'] = segment_end - current_seg['start_time']

                # Merge transcripts
                if segment_transcript:
                    if current_seg['transcript']:
                        current_seg['transcript'] += ' ' + segment_transcript
                    else:
                        current_seg['transcript'] = segment_transcript

                current_seg['segment_count'] += 1
            else:
                # Gap too large - save current and start new
                merged.append(current_seg)
                current_seg = {
                    'speaker_id': segment_speaker,
                    'start_time': segment_start,
                    'end_time': segment_end,
                    'duration': segment_end - segment_start,
                    'transcript': segment_transcript or '',
                    'segment_count': 1
                }
        else:
            # Different speaker - save current and start new
            merged.append(current_seg)
            current_seg = {
                'speaker_id': segment_speaker,
                'start_time': segment_start,
                'end_time': segment_end,
                'duration': segment_end - segment_start,
                'transcript': segment_transcript or '',
                'segment_count': 1
            }

    # Don't forget the last segment
    if current_seg is not None:
        merged.append(current_seg)

    return merged


async def process_meeting_task(meeting_id: str):
    """
    Background task to process a meeting with complete pipeline.

    Pipeline Stages (两阶段设计，后阶段失败不影响前阶段):
    ========================================================
    阶段1 - 人声分离 (10%-50%):
      - 初始化 (10%)
      - 人声分离进行中 (10-40%)
      - 人声分离完成 (50%) ← 第一个里程碑，数据入库

    阶段2 - 总结生成 (50%-100%):
      - AI 总结进行中 (50-90%)
      - 保存总结 (90-99%)
      - 处理完成 (100%) ← 第二个里程碑
    """
    _log_separator(f"STARTING PROCESSING TASK FOR MEETING: {meeting_id}")

    # =================================================================
    # PHASE 1: VOICE SEPARATION (10%-50%)
    # 此阶段失败会影响整体，但成功后数据会被保留
    # =================================================================
    async with AsyncSessionLocal() as db:
        try:
            # Get meeting
            logger.info(f"[{meeting_id}] Fetching meeting from database...")
            meeting = await meeting_repository.get(db, meeting_id)
            if not meeting:
                logger.error(f"[{meeting_id}] Meeting not found in database")
                return

            logger.info(f"[{meeting_id}] Meeting found: {meeting.title}")
            logger.info(f"[{meeting_id}] Audio path: {meeting.audio_path}")

            # STAGE 1: INITIALIZING (10%)
            logger.info(f"[{meeting_id}] Stage 1: INITIALIZING (10%)...")
            await meeting_repository.update_stage(
                db=db,
                meeting_id=meeting_id,
                status=MeetingStatus.PROCESSING,
                stage=ProcessingStage.INITIALIZING,
                progress=10
            )
            await db.commit()

            # =================================================================
            # STEP 1.1: Voice Separation (10-40%)
            # =================================================================
            _log_separator(f"[{meeting_id}] STEP 1.1: VOICE SEPARATION (10-40%)")
            await meeting_repository.update_stage(
                db=db,
                meeting_id=meeting_id,
                status=MeetingStatus.PROCESSING,
                stage=ProcessingStage.SEPARATING,
                progress=15
            )
            await db.commit()

            separation_result = await separation_service.separate_voices(
                audio_path=meeting.audio_path
            )

            logger.info(
                f"[{meeting_id}] Voice separation completed: "
                f"{len(separation_result.speakers)} speakers, "
                f"{len(separation_result.timeline)} segments"
            )

            # Log speaker details
            for speaker in separation_result.speakers:
                logger.info(
                    f"[{meeting_id}] - Speaker: {speaker.display_name} "
                    f"({speaker.speaker_id}), "
                    f"duration: {speaker.total_duration:.2f}s"
                )

            await meeting_repository.update_stage(
                db=db,
                meeting_id=meeting_id,
                status=MeetingStatus.PROCESSING,
                stage=ProcessingStage.SEPARATING,
                progress=40
            )
            await db.commit()

            # =================================================================
            # STEP 1.2: Create Participant Records (40-50%)
            #           人声分离完成后，参与者数据入库
            # =================================================================
            _log_separator(f"[{meeting_id}] STEP 1.2: SAVING PARTICIPANT DATA (40-50%)")

            # Store participant IDs mapping for creating speaker segments
            participant_id_map = {}
            participants_created = 0

            for speaker in separation_result.speakers:
                participant = await participant_repository.create(
                    db=db,
                    meeting_id=meeting_id,
                    speaker_id=speaker.speaker_id,
                    display_name=speaker.display_name,
                    voice_segment_path=None
                )
                participant_id_map[speaker.speaker_id] = participant.id
                participants_created += 1
                logger.debug(f"[{meeting_id}] Created participant: {speaker.display_name} -> {participant.id}")

            # =================================================================
            # STEP 1.3: Create Speaker Segment Records (保存发言片段)
            #           时间轴数据入库
            # =================================================================
            _log_separator(f"[{meeting_id}] STEP 1.3: SAVING SPEAKER SEGMENTS")
            segments_created = 0

            for idx, segment in enumerate(separation_result.timeline):
                participant_id = participant_id_map.get(segment.speaker_id)
                duration = segment.end_time - segment.start_time

                speaker_segment = SpeakerSegment(
                    meeting_id=meeting_id,
                    participant_id=participant_id,
                    speaker_id=segment.speaker_id,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    duration=duration,
                    transcript=segment.transcript,  # Save transcription from separation service
                    segment_index=idx
                )
                db.add(speaker_segment)
                segments_created += 1

                if (idx + 1) % 100 == 0:
                    logger.debug(f"[{meeting_id}] Saved {idx + 1}/{len(separation_result.timeline)} segments...")

            await db.flush()  # Flush without committing yet
            logger.info(f"[{meeting_id}] ✅ {segments_created} speaker segments saved to database")

            # =================================================================
            # STEP 1.4: MERGE CONSECUTIVE SEGMENTS
            # 合并同一人的连续发言片段（间隔超过1秒则分开）
            # =================================================================
            _log_separator(f"[{meeting_id}] STEP 1.4: MERGING CONSECUTIVE SEGMENTS")

            # 打印原始人声分离结果日志
            _log_separator(f"[{meeting_id}] 音频文件结果日志 (原始发言片段)")
            # for idx, seg in enumerate(separation_result.timeline, 1):
            #     speaker_num = seg.speaker_id.split('_')[1] if '_' in seg.speaker_id else seg.speaker_id
            #     start_min, start_sec = divmod(int(seg.start_time), 60)
            #     end_min, end_sec = divmod(int(seg.end_time), 60)
            #     duration = seg.end_time - seg.start_time
            #     transcript_preview = (seg.transcript[:100] + '...') if seg.transcript and len(seg.transcript) > 100 else (seg.transcript or '')
                # logger.info(
                #     f"[{meeting_id}] [{idx}] 说话人{speaker_num} | "
                #     f"时间: {start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d} | "
                #     f"时长: {duration:.1f}s | "
                #     f"内容: {transcript_preview}"
                # )
            _log_separator()

            merged_segments = _merge_consecutive_segments(separation_result.timeline)
            logger.info(f"[{meeting_id}] Merged {segments_created} original segments into {len(merged_segments)} combined segments")

            # Save merged segments to database
            merged_segments_created = 0
            for idx, merged_seg in enumerate(merged_segments):
                participant_id = participant_id_map.get(merged_seg['speaker_id'])

                merged_segment = MergedSegment(
                    meeting_id=meeting_id,
                    participant_id=participant_id,
                    speaker_id=merged_seg['speaker_id'],
                    start_time=merged_seg['start_time'],
                    end_time=merged_seg['end_time'],
                    duration=merged_seg['duration'],
                    transcript=merged_seg['transcript'],
                    segment_count=merged_seg['segment_count'],
                    segment_index=idx
                )
                db.add(merged_segment)
                merged_segments_created += 1

            await db.flush()
            logger.info(f"[{meeting_id}] ✅ {merged_segments_created} merged segments saved to database")

            # 更新会议时长
            if separation_result.duration:
                await meeting_repository.update_duration(
                    db=db,
                    meeting_id=meeting_id,
                    duration=separation_result.duration
                )

            # 🔥 关键：人声分离完成，设置为 50% 并提交到数据库
            # 此时即使后续阶段失败，参与者数据和时间轴数据也已保留
            await meeting_repository.update_stage(
                db=db,
                meeting_id=meeting_id,
                status=MeetingStatus.PROCESSING,
                stage=ProcessingStage.SEPARATION_COMPLETED,
                progress=50
            )
            await db.commit()
            logger.info(f"[{meeting_id}] ✅ STAGE 1 COMPLETED: Separation done (50%)")
            logger.info(f"[{meeting_id}] ✅ {participants_created} participants, {segments_created} segments saved")

        except Exception as e:
            logger.exception(f"[{meeting_id}] ERROR during voice separation phase: {e}")
            await db.rollback()

            # 阶段1失败，标记为失败
            async with AsyncSessionLocal() as error_db:
                await meeting_repository.update_stage(
                    db=error_db,
                    meeting_id=meeting_id,
                    status=MeetingStatus.FAILED,
                    stage=ProcessingStage.INITIALIZING,
                    progress=0,
                    error_message=f"人声分离失败: {str(e)}"
                )
                await error_db.commit()
            logger.error(f"[{meeting_id}] Meeting FAILED at separation stage")
            return

    # =================================================================
    # PHASE 2: SUMMARY GENERATION (50%-100%)
    # 此阶段失败不影响阶段1的数据
    # =================================================================
    async with AsyncSessionLocal() as db:
        try:
            # =================================================================
            # STEP 2.1: LLM Summary Generation (50-90%)
            # =================================================================
            _log_separator(f"[{meeting_id}] STEP 2.1: LLM SUMMARY GENERATION (50-90%)")
            logger.info(f"[{meeting_id}] Starting AI summary generation...")

            await meeting_repository.update_stage(
                db=db,
                meeting_id=meeting_id,
                status=MeetingStatus.PROCESSING,
                stage=ProcessingStage.SUMMARIZING,
                progress=55
            )
            await db.commit()

            # Generate summary using LLM with actual transcripts
            # Build merged segments with transcripts for LLM
            merged_for_llm = []
            for merged_seg in merged_segments:
                merged_for_llm.append(
                    SpeakerSegment(
                        speaker_id=merged_seg['speaker_id'],
                        start_time=merged_seg['start_time'],
                        end_time=merged_seg['end_time'],
                        transcript=merged_seg['transcript']
                    )
                )

            # Create speaker name mapping for proper display in prompt
            speaker_name_map = {
                s.speaker_id: s.display_name
                for s in separation_result.speakers
            }

            summary_content = await llm_service.generate_summary_from_timeline(
                audio_path=meeting.audio_path,
                speakers=separation_result.speakers,
                meeting_title=meeting.title,
                timeline=merged_for_llm,
                speaker_name_map=speaker_name_map
            )

            logger.info(f"[{meeting_id}] LLM summary generated: {len(summary_content.content)} chars")

            await meeting_repository.update_stage(
                db=db,
                meeting_id=meeting_id,
                status=MeetingStatus.PROCESSING,
                stage=ProcessingStage.SUMMARIZING,
                progress=90
            )
            await db.commit()

            # =================================================================
            # STEP 2.2: Save Summary (90-100%)
            # =================================================================
            _log_separator(f"[{meeting_id}] STEP 2.2: SAVING SUMMARY (90-100%)")

            await summary_repository.create(
                db=db,
                meeting_id=meeting_id,
                content=summary_content.content,
                raw_response=summary_content.raw_response
            )
            await db.commit()
            logger.info(f"[{meeting_id}] Summary saved to database")

            # 🔥 关键：全部完成，设置为 100%
            await meeting_repository.update_stage(
                db=db,
                meeting_id=meeting_id,
                status=MeetingStatus.COMPLETED,
                stage=ProcessingStage.COMPLETED,
                progress=100
            )
            await db.commit()

            _log_separator(f"[{meeting_id}] ✅ ALL STAGES COMPLETED SUCCESSFULLY ✅")
            logger.info(f"[{meeting_id}] Meeting processing complete (100%)")

        except Exception as e:
            logger.exception(f"[{meeting_id}] ERROR during summary generation phase: {e}")

            # 阶段2失败：不回滚阶段1的数据，只标记错误
            # 用户可以看到参与者数据，但知道总结生成失败
            async with AsyncSessionLocal() as error_db:
                await meeting_repository.update_stage(
                    db=error_db,
                    meeting_id=meeting_id,
                    status=MeetingStatus.FAILED,
                    stage=ProcessingStage.SEPARATION_COMPLETED,  # 保持在分离完成阶段
                    progress=50,  # 保持50%进度
                    error_message=f"总结生成失败 (人声分离已完成): {str(e)}"
                )
                await error_db.commit()

            logger.error(f"[{meeting_id}] Summary generation FAILED")
            logger.warning(f"[{meeting_id}] ⚠️  Voice separation data preserved at 50%")
            logger.warning(f"[{meeting_id}] ⚠️  Participant data still available")
