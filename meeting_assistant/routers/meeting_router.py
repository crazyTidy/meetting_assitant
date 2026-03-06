"""Meeting API endpoints."""
from typing import Optional
from pathlib import Path
import logging
from urllib.parse import quote
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Request, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..settings.database import get_db
from ..settings.config import settings
from ..utils.security_util import get_current_user
from ..items.meeting_item import (
    MeetingResponse,
    MeetingDetailResponse,
    MeetingListResponse,
    MeetingStatusResponse,
    ParticipantUpdate,
    ErrorResponse
)
from ..services.meeting_service import meeting_service, summary_service, regenerate_service, participant_service
logger = logging.getLogger(__name__)

router = APIRouter()


class SummaryUpdateRequest(BaseModel):
    """Request model for updating summary."""
    content: str


@router.post(
    "/",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        413: {"model": ErrorResponse, "description": "File too large"}
    }
)
async def create_meeting(
    background_tasks: BackgroundTasks,
    title: str = Form(..., min_length=1, max_length=255),
    audio: UploadFile = File(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Upload audio and create a new meeting.

    - **title**: Meeting title (required)
    - **audio**: Audio file (mp3, wav, m4a supported)

    Returns the created meeting with pending status.
    Processing starts automatically in the background.
    """
    try:
        # Get current user from request.state
        current_user = get_current_user(request)
        creator_id = current_user.get("user_id") if current_user else None

        meeting = await meeting_service.create_meeting(
            db=db,
            title=title,
            audio_file=audio,
            background_tasks=background_tasks,
            creator_id=creator_id
        )
        return meeting
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_INPUT", "message": str(e)}}
        )


@router.get(
    "/",
    response_model=MeetingListResponse
)
async def list_meetings(
    search: Optional[str] = None,
    page: int = 1,
    size: int = 10,
    creator_id: Optional[str] = None,
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of meetings.

    - **search**: Search by meeting title (optional)
    - **page**: Page number (default: 1)
    - **size**: Items per page (default: 10, max: 100)
    - **creator_id**: Filter by creator user ID (optional)
    """
    if page < 1:
        page = 1
    if size < 1:
        size = 1
    if size > 100:
        size = 100

    # If no creator_id specified, filter by current user
    if not creator_id:
        current_user = get_current_user(request)
        if current_user:
            creator_id = current_user.get("user_id")

    return await meeting_service.get_meeting_list(
        db=db,
        search=search,
        page=page,
        size=size,
        creator_id=creator_id
    )


@router.get(
    "/{meeting_id}",
    response_model=MeetingDetailResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get meeting details including participants and summary.

    - **meeting_id**: Meeting UUID
    """
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )
    return meeting


@router.get(
    "/{meeting_id}/status",
    response_model=MeetingStatusResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_meeting_status(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get meeting processing status.

    Use this endpoint to poll for processing progress.
    Recommended polling interval: 3 seconds.

    - **meeting_id**: Meeting UUID
    """
    status_response = await meeting_service.get_meeting_status(db, meeting_id)
    if not status_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )
    return status_response


@router.delete(
    "/{meeting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}}
)
async def delete_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a meeting and all associated data.

    - **meeting_id**: Meeting UUID
    """
    deleted = await meeting_service.delete_meeting(db, meeting_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )


@router.get(
    "/{meeting_id}/audio",
    responses={404: {"model": ErrorResponse}}
)
async def download_audio(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download the original audio file for a meeting.

    - **meeting_id**: Meeting UUID
    """
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )

    audio_path = Path(meeting.audio_path)
    if not audio_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "FILE_NOT_FOUND", "message": "音频文件不存在"}}
        )

    # Determine media type based on file extension
    media_type = "audio/mpeg"
    if audio_path.suffix == ".wav":
        media_type = "audio/wav"
    elif audio_path.suffix == ".m4a":
        media_type = "audio/mp4"
    elif audio_path.suffix == ".flac":
        media_type = "audio/flac"
    elif audio_path.suffix == ".ogg":
        media_type = "audio/ogg"

    # Create filename from title
    safe_title = "".join(c for c in meeting.title if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{safe_title}{audio_path.suffix}"

    # Use RFC 5987 encoding for non-ASCII filenames
    encoded_filename = quote(filename)

    return FileResponse(
        path=str(audio_path),
        media_type=media_type,
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )


@router.patch(
    "/{meeting_id}/summary",
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}}
)
async def update_summary(
    meeting_id: str,
    request: SummaryUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update meeting summary content.

    - **meeting_id**: Meeting UUID
    - **content**: New summary content in Markdown format
    """
    # Verify meeting exists
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )

    # Update summary
    updated = await summary_service.update_summary(
        db=db,
        meeting_id=meeting_id,
        content=request.content
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "SUMMARY_NOT_FOUND", "message": "会议纪要不存在"}}
        )

    await db.commit()

    return updated


@router.post(
    "/{meeting_id}/regenerate-summary",
    response_model=MeetingStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorResponse, "description": "Cannot regenerate summary"},
        404: {"model": ErrorResponse, "description": "Meeting not found"}
    }
)
async def regenerate_summary(
    meeting_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Regenerate meeting summary using existing speaker segments.

    This endpoint triggers a background task to regenerate the AI summary
    based on the existing speaker timeline data. Useful when you want to
    improve the summary quality or the original generation failed.

    - **meeting_id**: Meeting UUID

    Returns the processing status. The actual generation happens in background.
    """
    result = await regenerate_service.regenerate_summary(
        db=db,
        meeting_id=meeting_id,
        background_tasks=background_tasks
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )

    return result


@router.get(
    "/{meeting_id}/download-docx",
    responses={
        404: {"model": ErrorResponse, "description": "Meeting or summary not found"}
    }
)
async def download_docx(
    meeting_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Download meeting summary as DOCX file.

    Generates a DOCX file following Chinese official document standards:
    - A4 paper, 2.54cm margins
    - Font: 仿宋_GB2312 for body, 黑体 for titles, 楷体GB2312 for level-2 headings
    - Font size: 三号 (16pt)
    - Line spacing: 28pt

    - **meeting_id**: Meeting UUID
    """
    from ..utils.docx_util import generate_meeting_minutes_docx
    from fastapi.responses import Response
    from pathlib import Path
    from urllib.parse import quote

    # Get meeting with summary
    meeting = await meeting_service.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "会议不存在"}}
        )

    if not meeting.summary or not meeting.summary.content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "SUMMARY_NOT_FOUND", "message": "会议纪要不存在"}}
        )

    # Generate DOCX
    try:
        docx_bytes = generate_meeting_minutes_docx(
            meeting_title=meeting.title,
            content=meeting.summary.content
        )

        # Create filename
        safe_title = "".join(c for c in meeting.title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{safe_title}_会议纪要.docx"
        encoded_filename = quote(filename)

        # Return file response
        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    except Exception as e:
        logger.error(f"[DOCX] Failed to generate document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "DOCX_GENERATION_FAILED", "message": "文档生成失败"}}
        )


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
    """Update speaker display name."""
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
