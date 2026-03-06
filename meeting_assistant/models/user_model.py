"""User database model."""
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship

from ..settings.database import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(String(100), primary_key=True)
    username = Column(String(100), nullable=True)
    real_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    department_id = Column(String(100), nullable=True)
    department_name = Column(String(100), nullable=True)
    position = Column(String(50), nullable=True)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    created_meetings = relationship("Meeting", back_populates="creator", foreign_keys="Meeting.creator_id")
