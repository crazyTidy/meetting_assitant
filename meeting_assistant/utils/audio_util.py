"""Audio utility functions."""
import subprocess
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


async def get_audio_duration(file_path: str) -> Optional[int]:
    """Get audio duration using ffprobe."""
    if not Path(file_path).exists():
        logger.warning(f"Audio file not found: {file_path}")
        return None

    try:
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", file_path]
        result = subprocess.run(cmd, capture_output=True, timeout=30, encoding='utf-8', errors='ignore')

        if result.returncode != 0:
            logger.warning(f"ffprobe failed for {file_path}: {result.stderr}")
            return None

        if not result.stdout or not result.stdout.strip():
            logger.warning(f"ffprobe returned empty output for {file_path}")
            return None

        data = json.loads(result.stdout)
        duration_str = data.get("format", {}).get("duration")

        if duration_str:
            return int(float(duration_str))

        return None

    except subprocess.TimeoutExpired:
        logger.error(f"ffprobe timeout for {file_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse ffprobe output: {e}")
        return None
    except FileNotFoundError:
        logger.error("ffprobe not found. Please install ffmpeg.")
        return None
    except Exception as e:
        logger.error(f"Error getting audio duration: {e}")
        return None
