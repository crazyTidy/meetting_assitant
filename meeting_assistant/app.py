"""Application entry point."""
import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from .settings.config import settings
from .settings.database import init_db
from .middlewares.dev_auth import dev_auth_middleware
from .middlewares.auth import auth_middleware
from .routers import meeting_router, user_router, participant_router, demo_router


def setup_logging():
    """Configure application logging."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=log_level, format=log_format, handlers=[logging.StreamHandler(sys.stdout)])
    logging.info(f"Logging configured at {logging.getLevelName(log_level)} level")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    setup_logging()
    await init_db()
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.DEV_MODE:
    app.middleware("http")(dev_auth_middleware)
else:
    app.middleware("http")(auth_middleware)

app.include_router(meeting_router.router, prefix=f"{settings.API_V1_STR}/meetings", tags=["meetings"])
app.include_router(user_router.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(participant_router.router, prefix=f"{settings.API_V1_STR}/participants", tags=["participants"])
app.include_router(demo_router.router, prefix=f"{settings.API_V1_STR}/demo", tags=["demo"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}
