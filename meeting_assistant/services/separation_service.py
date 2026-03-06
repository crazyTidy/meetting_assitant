"""Voice separation service."""
import logging
from typing import List, Optional
from dataclasses import dataclass
import aiohttp
import asyncio
from pathlib import Path

from ..settings.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SpeakerSegment:
    """A time-stamped segment of speech from a speaker."""
    speaker_id: str
    start_time: float  # seconds
    end_time: float    # seconds
    audio_segment_path: Optional[str] = None  # Path to separated audio segment
    transcript: Optional[str] = None  # Transcription text for this segment


@dataclass
class SpeakerInfo:
    """Speaker information from separation."""
    speaker_id: str
    display_name: str
    segments: List[SpeakerSegment]  # All segments for this speaker, ordered by time
    total_duration: float = 0.0  # Total speaking time in seconds


@dataclass
class SeparationResult:
    """Result from voice separation."""
    speakers: List[SpeakerInfo]
    timeline: List[SpeakerSegment]  # All segments from all speakers, sorted by start_time
    duration: Optional[int] = None  # Total meeting duration in seconds


class SeparationService:
    """Service for voice separation using third-party API."""

    def __init__(self):
        self.api_key = settings.SEPARATION_API_KEY
        self.api_url = settings.SEPARATION_API_URL

    async def separate_voices(self, audio_path: str) -> SeparationResult:
        """
        Separate voices from audio file with timestamp information.

        This calls the configured third-party API for speaker diarization.

        Returns:
            SeparationResult with timeline of speaker segments
        """
        logger.info(f"[VOICE_SEPARATION] Starting voice separation for audio: {audio_path}")
        logger.info(f"[VOICE_SEPARATION] API URL: {self.api_url}")
        logger.info(f"[VOICE_SEPARATION] API Key configured: {bool(self.api_key)}")

        try:
            # Get file extension for proper MIME type
            file_ext = Path(audio_path).suffix.lower()
            mime_type_map = {
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.m4a': 'audio/mp4',
                '.flac': 'audio/flac',
                '.ogg': 'audio/ogg'
            }
            mime_type = mime_type_map.get(file_ext, 'audio/mpeg')

            logger.info(f"[VOICE_SEPARATION] Opening audio file and sending API request...")
            logger.info(f"[VOICE_SEPARATION] File: {Path(audio_path).name}, MIME type: {mime_type}")

            # Use aiohttp for better compatibility with the API
            timeout = aiohttp.ClientTimeout(total=300, connect=30, sock_read=300)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                with open(audio_path, 'rb') as f:
                    file_content = f.read()

                    # Prepare form data
                    data = aiohttp.FormData()
                    data.add_field(
                        'file',
                        file_content,
                        filename=Path(audio_path).name,
                        content_type=mime_type
                    )
                    data.add_field('enable_diarization', 'true')

                    headers = {}
                    if self.api_key:
                        headers["Authorization"] = f"Bearer {self.api_key}"

                    logger.debug(f"[VOICE_SEPARATION] Request data: enable_diarization=true")
                    logger.debug(f"[VOICE_SEPARATION] API URL: {self.api_url}")

                    async with session.post(
                        self.api_url,
                        data=data,
                        headers=headers
                    ) as response:
                        logger.info(f"[VOICE_SEPARATION] API response status: {response.status}")

                        response_text = await response.text()
                        logger.info(f"[VOICE_SEPARATION] API response: {response_text[:5000]}")

                        if response.status != 200:
                            logger.error(f"[VOICE_SEPARATION] API request failed with status {response.status}")
                            logger.error(f"[VOICE_SEPARATION] Response body: {response_text}")
                            raise Exception(f"Speaker diarization API failed: {response.status} - {response_text}")

                        result = await response.json()
                        logger.info(f"[VOICE_SEPARATION] API response received, parsing results...")

                # Check API response code
                if result.get("code") != 0:
                    error_msg = result.get("message", "Unknown error")
                    logger.error(f"[VOICE_SEPARATION] API returned error code {result.get('code')}: {error_msg}")
                    raise Exception(f"Speaker diarization API error: {error_msg}")

                # Parse API response to extract speaker segments with timestamps
                data_obj = result.get("data", {})
                api_segments = data_obj.get("segments", [])

                segments = []
                speakers_dict = {}

                for seg_data in api_segments:
                    # Convert speaker number (0, 1, etc.) to speaker_id format (speaker_1, speaker_2, etc.)
                    speaker_num = seg_data.get("speaker", 0)
                    speaker_id = f"speaker_{speaker_num + 1}"

                    # Convert milliseconds to seconds
                    start_time = seg_data.get("start_ms", 0) / 1000.0
                    end_time = seg_data.get("end_ms", 0) / 1000.0

                    segment = SpeakerSegment(
                        speaker_id=speaker_id,
                        start_time=start_time,
                        end_time=end_time,
                        audio_segment_path=None,
                        transcript=seg_data.get("text")
                    )
                    segments.append(segment)

                    # Organize by speaker
                    if speaker_id not in speakers_dict:
                        speakers_dict[speaker_id] = []
                    speakers_dict[speaker_id].append(segment)

                logger.info(f"[VOICE_SEPARATION] Parsed {len(segments)} segments, {len(speakers_dict)} speakers")

                # =================================================================
                # FALLBACK: If no speakers detected, create a default speaker
                # =================================================================
                if len(segments) == 0 or len(speakers_dict) == 0:
                    logger.warning(f"[VOICE_SEPARATION] No speakers detected in audio, creating default speaker")
                    logger.warning(f"[VOICE_SEPARATION] API response: {result}")

                    total_duration_ms = data_obj.get("total_duration_ms", 60000)
                    default_duration = total_duration_ms / 1000.0

                    default_segment = SpeakerSegment(
                        speaker_id="speaker_1",
                        start_time=0.0,
                        end_time=default_duration
                    )
                    segments.append(default_segment)
                    speakers_dict["speaker_1"] = [default_segment]

                    logger.info(f"[VOICE_SEPARATION] Created default speaker: speaker_1, duration: {default_duration}s")

            # Create speaker info with calculated total duration
            speakers = []
            for speaker_id, speaker_segments in speakers_dict.items():
                total_duration = sum(seg.end_time - seg.start_time for seg in speaker_segments)
                speaker_num = speaker_id.split("_")[1] if "_" in speaker_id else "1"
                display_name = f"说话人{speaker_num}"

                logger.debug(f"[VOICE_SEPARATION] Speaker {speaker_id}: {len(speaker_segments)} segments, total duration: {total_duration:.2f}s")

                speakers.append(SpeakerInfo(
                    speaker_id=speaker_id,
                    display_name=display_name,
                    segments=speaker_segments,
                    total_duration=total_duration
                ))

            # Sort timeline by start time
            timeline = sorted(segments, key=lambda s: s.start_time)

            # Get duration from API response (convert from milliseconds to seconds)
            duration = data_obj.get("total_duration_ms")
            if duration:
                duration = duration / 1000.0  # Convert to seconds

            logger.info(f"[VOICE_SEPARATION] Voice separation completed successfully")
            logger.info(f"[VOICE_SEPARATION] Total speakers: {len(speakers)}, total segments: {len(timeline)}, duration: {duration}s")

            return SeparationResult(
                speakers=speakers,
                timeline=timeline,
                duration=duration
            )

        except FileNotFoundError as e:
            logger.error(f"[VOICE_SEPARATION] Audio file not found: {audio_path}")
            raise
        except asyncio.TimeoutError:
            logger.error(f"[VOICE_SEPARATION] API request timeout after 300 seconds")
            raise
        except aiohttp.ClientConnectorError as e:
            logger.error(f"[VOICE_SEPARATION] Failed to connect to API server: {e}")
            logger.error(f"[VOICE_SEPARATION] API URL: {self.api_url}")
            logger.error(f"[VOICE_SEPARATION] Please check if the API server is running and accessible")
            raise
        except Exception as e:
            logger.exception(f"[VOICE_SEPARATION] Unexpected error during voice separation: {e}")
            raise


# Singleton instance
separation_service = SeparationService()
