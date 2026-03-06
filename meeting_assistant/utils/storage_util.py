"""Storage utility for local and MinIO storage."""
import uuid
import aiofiles
from pathlib import Path
from typing import Optional, BinaryIO
import logging

from ..settings.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Storage service supporting local and MinIO."""

    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        if self.storage_type == "minio":
            from .clients.minio_client import MinioClient
            self.minio_client = MinioClient()
            self._ensure_bucket()

    def _ensure_bucket(self):
        """Ensure MinIO bucket exists."""
        try:
            buckets = self.minio_client.list_buckets()
            if not any(b.name == settings.MINIO_BUCKET for b in buckets):
                self.minio_client.create_bucket(settings.MINIO_BUCKET)
                logger.info(f"Created MinIO bucket: {settings.MINIO_BUCKET}")
        except Exception as e:
            logger.error(f"Failed to ensure bucket: {e}")

    async def save_file(self, file_content: bytes, filename: str) -> str:
        """Save file and return storage path."""
        if self.storage_type == "minio":
            return await self._save_to_minio(file_content, filename)
        else:
            return await self._save_to_local(file_content, filename)

    async def _save_to_local(self, file_content: bytes, filename: str) -> str:
        """Save file to local storage."""
        file_path = Path(settings.UPLOAD_DIR) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        return str(file_path)

    async def _save_to_minio(self, file_content: bytes, filename: str) -> str:
        """Save file to MinIO."""
        temp_path = Path(settings.UPLOAD_DIR) / f"temp_{uuid.uuid4()}"
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(file_content)

        success = await self.minio_client.async_upload_file(
            settings.MINIO_BUCKET, filename, str(temp_path)
        )
        temp_path.unlink()

        if success:
            return f"minio://{settings.MINIO_BUCKET}/{filename}"
        raise Exception("Failed to upload to MinIO")

    async def get_file_path(self, storage_path: str) -> str:
        """Get actual file path for processing."""
        if storage_path.startswith("minio://"):
            return await self._download_from_minio(storage_path)
        return storage_path

    async def _download_from_minio(self, storage_path: str) -> str:
        """Download file from MinIO to temp location."""
        object_name = storage_path.replace(f"minio://{settings.MINIO_BUCKET}/", "")
        temp_path = Path(settings.UPLOAD_DIR) / f"temp_{uuid.uuid4()}_{Path(object_name).name}"
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        success = await self.minio_client.async_download_file(
            settings.MINIO_BUCKET, object_name, str(temp_path)
        )
        if success:
            return str(temp_path)
        raise Exception("Failed to download from MinIO")

    async def delete_file(self, storage_path: str) -> bool:
        """Delete file from storage."""
        if storage_path.startswith("minio://"):
            object_name = storage_path.replace(f"minio://{settings.MINIO_BUCKET}/", "")
            return await self.minio_client.async_remove_file(settings.MINIO_BUCKET, object_name)
        else:
            try:
                Path(storage_path).unlink(missing_ok=True)
                return True
            except Exception as e:
                logger.error(f"Failed to delete local file: {e}")
                return False


storage_service = StorageService()
