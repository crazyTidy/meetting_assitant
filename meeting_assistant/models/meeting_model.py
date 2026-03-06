"""Meeting database model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
import enum

from ..settings.database import Base


class MeetingStatus(str, enum.Enum):
    """Meeting processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStage(str, enum.Enum):
    """Processing stage for progress tracking."""
    INITIALIZING = "initializing"
    SEPARATING = "separating"
    SEPARATION_COMPLETED = "separation_completed"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"


class Meeting(Base):
    """Meeting model."""

    __tablename__ = "meetings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    audio_path = Column(String(512), nullable=False)
    creator_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(MeetingStatus), default=MeetingStatus.PENDING, nullable=False)
    progress = Column(Integer, default=0)
    stage = Column(String(50), default=ProcessingStage.INITIALIZING, nullable=True)
    error_message = Column(Text, nullable=True)
    duration = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    creator = relationship("User", back_populates="created_meetings", foreign_keys=[creator_id])
    participants = relationship("Participant", back_populates="meeting", cascade="all, delete-orphan")
    summary = relationship("Summary", back_populates="meeting", uselist=False, cascade="all, delete-orphan")
    speaker_segments = relationship("SpeakerSegment", back_populates="meeting", cascade="all, delete-orphan", order_by="SpeakerSegment.start_time")
    merged_segments = relationship("MergedSegment", back_populates="meeting", cascade="all, delete-orphan", order_by="MergedSegment.start_time")
