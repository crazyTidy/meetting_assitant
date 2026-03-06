"""Development mode authentication middleware."""
from fastapi import Request
from ..settings.config import settings


async def dev_auth_middleware(request: Request, call_next):
    """Development mode authentication middleware."""
    if settings.DEV_MODE:
        request.state.user = {
            "user_id": settings.DEV_USER_ID,
            "username": settings.DEV_USERNAME,
            "real_name": settings.DEV_REAL_NAME,
            "email": None,
            "phone": None,
            "department_id": None,
            "department_name": None,
            "position": None
        }
    response = await call_next(request)
    return response
