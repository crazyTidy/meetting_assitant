"""Application configuration settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Meeting Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API
    API_V1_STR: str = "/api/v1"

    # Database Configuration
    DATABASE_TYPE: str = "sqlite"

    # SQLite (default)
    SQLITE_DB_PATH: str = "./meeting_assistant.db"

    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "meeting_assistant"
    POSTGRES_POOL_SIZE: int = 5
    POSTGRES_MAX_OVERFLOW: int = 10

    @property
    def DATABASE_URL(self) -> str:
        """Generate database URL based on DATABASE_TYPE."""
        if self.DATABASE_TYPE == "postgresql":
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        else:
            return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"

    # File Upload
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024
    ALLOWED_AUDIO_EXTENSIONS: set = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}

    # Storage Configuration
    STORAGE_TYPE: str = "local"  # Options: local, minio

    # MinIO Configuration
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "meeting-assistant"
    MINIO_SECURE: bool = False

    # External APIs
    ZHIPU_API_KEY: str = "bd0265bc4e17414da4fbfa64ed303a46.2pUrRsJ5sQhpTHAY"
    SEPARATION_API_KEY: str = ""
    SEPARATION_API_URL: str = "http://192.168.0.100:40901/recognize"
    ASR_API_KEY: str = ""
    ASR_API_URL: str = ""
    # Task Processing
    TASK_RETRY_COUNT: int = 3
    TASK_POLLING_INTERVAL: int = 3

    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # Development Mode
    DEV_MODE: bool = False
    DEV_USER_ID: str = "dev-user-001"
    DEV_USERNAME: str = "dev_user"
    DEV_REAL_NAME: str = "开发测试用户"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
