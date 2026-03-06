"""Meeting item schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from ..models.meeting_model import MeetingStatus, ProcessingStage


class CreatorInfo(BaseModel):
    """Creator information schema."""
    id: str
    username: Optional[str] = None
    real_name: Optional[str] = None
    department_name: Optional[str] = None

    class Config:
        from_attributes = True


class ParticipantBase(BaseModel):
    """Base participant schema."""
    speaker_id: str
    display_name: str


class ParticipantCreate(ParticipantBase):
    """Schema for creating a participant."""
    voice_segment_path: Optional[str] = None


class ParticipantUpdate(BaseModel):
    """Schema for updating a participant."""
    display_name: str = Field(..., min_length=1, max_length=100)


class ParticipantResponse(ParticipantBase):
    """Schema for participant response."""
    id: str
    voice_segment_path: Optional[str] = None

    class Config:
        from_attributes = True


class SpeakerSegmentResponse(BaseModel):
    """Schema for speaker segment response."""
    id: str
    participant_id: Optional[str] = None
    speaker_id: str
    start_time: float
    end_time: float
    duration: float
    transcript: Optional[str] = None
    segment_index: Optional[int] = None

    class Config:
        from_attributes = True


class MergedSegmentResponse(BaseModel):
    """Schema for merged segment response."""
    id: str
    participant_id: Optional[str] = None
    speaker_id: str
    start_time: float
    end_time: float
    duration: float
    transcript: Optional[str] = None
    segment_count: int
    segment_index: int

    class Config:
        from_attributes = True


class SummaryBase(BaseModel):
    """Base summary schema."""
    content: str


class SummaryResponse(SummaryBase):
    """Schema for summary response."""
    id: str
    generated_at: datetime

    class Config:
        from_attributes = True


class MeetingCreate(BaseModel):
    """Schema for creating a meeting."""
    title: str = Field(..., min_length=1, max_length=255)
    audio_path: str


class MeetingResponse(BaseModel):
    """Schema for meeting response."""
    id: str
    title: str
    status: MeetingStatus
    progress: int
    stage: Optional[ProcessingStage] = None
    duration: Optional[float] = None
    creator_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MeetingDetailResponse(MeetingResponse):
    """Schema for detailed meeting response."""
    creator: Optional[CreatorInfo] = None
    participants: List[ParticipantResponse] = []
    speaker_segments: List[SpeakerSegmentResponse] = []
    merged_segments: List[MergedSegmentResponse] = []
    summary: Optional[SummaryResponse] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class MeetingStatusResponse(BaseModel):
    """Schema for meeting status response."""
    id: str
    status: MeetingStatus
    progress: int
    stage: Optional[ProcessingStage] = None
    message: str
    stage_description: Optional[str] = None

class MeetingListResponse(BaseModel):
    """Schema for paginated meeting list."""
    items: List[MeetingResponse]
    total: int
    page: int
    size: int
    pages: int


class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: dict = Field(..., example={"code": "VALIDATION_ERROR", "message": "Invalid input"})
