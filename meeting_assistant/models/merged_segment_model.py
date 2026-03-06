"""Merged speaker segment database model."""
import uuid
from sqlalchemy import Column, String, Float, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from ..settings.database import Base


class MergedSegment(Base):
    """Merged speaker segment model."""

    __tablename__ = "merged_segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    participant_id = Column(String(36), ForeignKey("participants.id", ondelete="SET NULL"), nullable=True)
    speaker_id = Column(String(50), nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    transcript = Column(Text, nullable=True)
    segment_count = Column(Integer, nullable=False, default=1)
    segment_index = Column(Integer, nullable=False)

    meeting = relationship("Meeting", back_populates="merged_segments")
    participant = relationship("Participant", foreign_keys=[participant_id])
