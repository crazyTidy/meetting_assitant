"""Speaker Segment database model."""
import uuid
from sqlalchemy import Column, String, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from ..settings.database import Base


class SpeakerSegment(Base):
    """Speaker segment model."""

    __tablename__ = "speaker_segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True)
    participant_id = Column(String(36), ForeignKey("participants.id", ondelete="CASCADE"), nullable=True)
    speaker_id = Column(String(50), nullable=False, index=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    transcript = Column(Text, nullable=True)
    segment_index = Column(Integer, nullable=True)

    meeting = relationship("Meeting", back_populates="speaker_segments")
    participant = relationship("Participant")
