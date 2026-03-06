"""ASR (Automatic Speech Recognition) service for transcribing audio."""
import logging
from typing import List, Optional
from dataclasses import dataclass
import httpx

from ..settings.config import settings
from .separation_service import SpeakerSegment

logger = logging.getLogger(__name__)


@dataclass
class TranscriptSegment:
    """A transcribed segment of speech with metadata."""
    speaker_id: str
    start_time: float  # seconds
    end_time: float    # seconds
    text: str          # Transcribed text
    confidence: float = 1.0  # Transcription confidence (0-1)


@dataclass
class TranscriptResult:
    """Complete transcript organized by timeline."""
    segments: List[TranscriptSegment]  # Ordered by start_time
    full_text: str  # Complete transcript as plain text


class ASRService:
    """Service for automatic speech recognition."""

    def __init__(self):
        self.api_key = settings.ASR_API_KEY
        self.api_url = settings.ASR_API_URL

    async def transcribe_audio(
        self,
        audio_path: str,
        timeline: List[SpeakerSegment]
    ) -> TranscriptResult:
        """
        Transcribe audio file using ASR service.

        This calls the configured ASR API for speech-to-text conversion.

        Args:
            audio_path: Path to the audio file
            timeline: Timeline of speaker segments from voice separation

        Returns:
            TranscriptResult with time-aligned transcriptions
        """
        logger.info(f"[ASR_TRANSCRIPTION] Starting audio transcription: {audio_path}")
        logger.info(f"[ASR_TRANSCRIPTION] API URL: {self.api_url}")
        logger.info(f"[ASR_TRANSCRIPTION] API Key configured: {bool(self.api_key)}")
        logger.info(f"[ASR_TRANSCRIPTION] Timeline segments to transcribe: {len(timeline)}")

        try:
            # Real API call to ASR service
            async with httpx.AsyncClient(timeout=600.0) as client:
                logger.info(f"[ASR_TRANSCRIPTION] Opening audio file and sending API request...")

                with open(audio_path, 'rb') as f:
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    data = {
                        "language": "zh",
                        "response_format": "verbose_json",
                        "timestamp_granularities": ["segment"]
                    }
                    files = {"file": f}

                    logger.debug(f"[ASR_TRANSCRIPTION] Request headers: {headers}")
                    logger.debug(f"[ASR_TRANSCRIPTION] Request data: {data}")

                    response = await client.post(
                        self.api_url,
                        headers=headers,
                        files=files,
                        data=data
                    )

                    logger.info(f"[ASR_TRANSCRIPTION] API response status: {response.status_code}")

                    if response.status_code != 200:
                        logger.error(f"[ASR_TRANSCRIPTION] API request failed with status {response.status_code}")
                        logger.error(f"[ASR_TRANSCRIPTION] Response body: {response.text}")
                        raise Exception(f"ASR API failed: {response.status_code} - {response.text}")

                    result = response.json()
                    logger.info(f"[ASR_TRANSCRIPTION] API response received, parsing results...")

                # Parse API response and align with speaker timeline
                # Assuming API returns something like:
                # {
                #   "segments": [
                #     {"start": 0.0, "end": 45.2, "text": "...", "confidence": 0.95},
                #     ...
                #   ],
                #   "full_text": "..."
                # }

                api_segments = result.get("segments", [])
                logger.info(f"[ASR_TRANSCRIPTION] API returned {len(api_segments)} transcript segments")

                # Create transcript segments aligned with speaker timeline
                segments = []
                full_text_parts = []

                for i, speaker_seg in enumerate(timeline):
                    # Find corresponding transcript segment based on time overlap
                    transcript_text = ""
                    confidence = 0.0

                    for api_seg in api_segments:
                        # Check if this API segment overlaps with the speaker segment
                        if (api_seg["start"] >= speaker_seg.start_time and
                            api_seg["start"] < speaker_seg.end_time):
                            transcript_text += api_seg["text"]
                            confidence = max(confidence, api_seg.get("confidence", 0.0))

                    segment = TranscriptSegment(
                        speaker_id=speaker_seg.speaker_id,
                        start_time=speaker_seg.start_time,
                        end_time=speaker_seg.end_time,
                        text=transcript_text.strip(),
                        confidence=confidence
                    )
                    segments.append(segment)

                    # Build full text with speaker labels
                    speaker_num = speaker_seg.speaker_id.split("_")[1] if "_" in speaker_seg.speaker_id else "1"
                    time_str = self._format_timestamp(speaker_seg.start_time)
                    full_text_parts.append(f"[{time_str}] 说话人{speaker_num}: {transcript_text.strip()}")

                    logger.debug(f"[ASR_TRANSCRIPTION] Segment {i+1}: speaker={speaker_seg.speaker_id}, time={speaker_seg.start_time:.1f}-{speaker_seg.end_time:.1f}s, text_length={len(transcript_text)}")

                full_text = "\n\n".join(full_text_parts)

                logger.info(f"[ASR_TRANSCRIPTION] Transcription completed successfully")
                logger.info(f"[ASR_TRANSCRIPTION] Total segments transcribed: {len(segments)}")
                logger.info(f"[ASR_TRANSCRIPTION] Full text length: {len(full_text)} characters")

                return TranscriptResult(
                    segments=segments,
                    full_text=full_text
                )

        except FileNotFoundError as e:
            logger.error(f"[ASR_TRANSCRIPTION] Audio file not found: {audio_path}")
            raise
        except httpx.TimeoutException:
            logger.error(f"[ASR_TRANSCRIPTION] API request timeout after 600 seconds")
            raise
        except Exception as e:
            logger.exception(f"[ASR_TRANSCRIPTION] Unexpected error during transcription: {e}")
            raise

    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp as MM:SS."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"


# Singleton instance
asr_service = ASRService()
