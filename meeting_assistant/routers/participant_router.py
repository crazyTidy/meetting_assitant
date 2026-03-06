"""Participant API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..settings.database import get_db
from ..items.meeting_item import ParticipantUpdate, ParticipantResponse, ErrorResponse
from ..services.meeting_service import participant_service

router = APIRouter()


@router.patch(
    "/{meeting_id}/participants/{participant_id}",
    response_model=ParticipantResponse,
    responses={404: {"model": ErrorResponse}}
)
async def update_participant_name(
    meeting_id: str,
    participant_id: str,
    participant_update: ParticipantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update participant display name.

    - **meeting_id**: Meeting UUID
    - **participant_id**: Participant UUID
    - **display_name**: New display name for the participant
    """
    result = await participant_service.update_participant_name(
        db=db,
        meeting_id=meeting_id,
        participant_id=participant_id,
        display_name=participant_update.display_name
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "参与者不存在"}}
        )

    return result


@router.patch(
    "/{meeting_id}/speakers/{speaker_id}/name",
    responses={404: {"model": ErrorResponse}}
)
async def update_speaker_name(
    meeting_id: str,
    speaker_id: str,
    participant_update: ParticipantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update display name for all participants with the same speaker_id.

    This updates all participants (across all meetings) that have the given speaker_id.
    Use this to rename a speaker globally.

    - **meeting_id**: Meeting UUID (for validation)
    - **speaker_id**: Speaker identifier (e.g., "speaker_1")
    - **display_name**: New display name for the speaker
    """
    result = await participant_service.update_participant_name_by_speaker_id(
        db=db,
        speaker_id=speaker_id,
        display_name=participant_update.display_name
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "说话人不存在"}}
        )

    return {"updated_count": result, "speaker_id": speaker_id}

