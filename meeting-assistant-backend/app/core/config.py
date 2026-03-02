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
    # Options: sqlite, postgresql
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
        else:  # sqlite
            return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"

    # File Upload
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_AUDIO_EXTENSIONS: set = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}

    # External APIs
    ZHIPU_API_KEY: str = "dc27759f5b5a4107b6af67aaf60e4a23.DmhTXSW9nk0eL74y"
    SEPARATION_API_KEY: str = ""
    SEPARATION_API_URL: str = "http://192.168.0.100:40901/recognize"  # Example local URL
    ASR_API_KEY: str = ""  # API key for ASR service (e.g., OpenAI Whisper, iFLYTEK)
    ASR_API_URL: str = ""  # ASR service endpoint

    # Task Processing
    TASK_RETRY_COUNT: int = 3
    TASK_POLLING_INTERVAL: int = 3  # seconds

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
