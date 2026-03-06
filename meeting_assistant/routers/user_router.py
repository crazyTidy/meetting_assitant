"""User API endpoints."""
from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse

from ..utils.security_util import get_current_user
from ..settings.config import settings
from ..items.user_item import (
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
    ConfigResponse
)

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(request: Request, login_data: LoginRequest):
    """
    Login endpoint supporting both token and dev mode.

    Args:
        request: FastAPI Request object
        login_data: Login request containing token or dev_mode flag

    Returns:
        Login response with access_token and user info
    """
    # Explicit dev mode login (when client sends dev_mode=true)
    if login_data.dev_mode is True:
        dev_user = CurrentUserResponse(
            user_id=settings.DEV_USER_ID,
            username=settings.DEV_USERNAME,
            real_name=settings.DEV_REAL_NAME,
            email=None,
            phone=None,
            department_id=None,
            department_name=None,
            position=None
        )
        return LoginResponse(
            access_token=None,  # Dev mode doesn't need token
            token_type=None,
            user=dev_user
        )

    # Token login
    if not login_data.token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "MISSING_TOKEN", "message": "Token is required"}}
        )

    # Validate token
    from ..utils.jwt_util import validate_token
    user_info = validate_token(login_data.token)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_TOKEN", "message": "Invalid or expired token"}}
        )

    # Return user info with token
    user_response = CurrentUserResponse(
        user_id=user_info.get("user_id", ""),
        username=user_info.get("username"),
        real_name=user_info.get("real_name"),
        email=user_info.get("email"),
        phone=user_info.get("phone"),
        department_id=user_info.get("department_id"),
        department_name=user_info.get("department_name"),
        position=user_info.get("position")
    )

    return LoginResponse(
        access_token=login_data.token,
        token_type="bearer",
        user=user_response
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user_info(
    request: Request
):
    """
    Get current authenticated user information.

    Returns the user information from the JWT token or development mode.
    """
    user = get_current_user(request)

    if not user:
        return JSONResponse(
            status_code=401,
            content={"error": {"code": "NOT_AUTHENTICATED", "message": "未认证"}}
        )

    # Return current user info
    return CurrentUserResponse(
        user_id=user.get("user_id", ""),
        username=user.get("username"),
        real_name=user.get("real_name"),
        email=user.get("email"),
        phone=user.get("phone"),
        department_id=user.get("department_id"),
        department_name=user.get("department_name"),
        position=user.get("position")
    )


@router.get("/config", response_model=ConfigResponse)
async def get_app_config():
    """
    Get application configuration for frontend.

    Returns development mode status and other non-sensitive configuration.
    """
    dev_user_info = None
    if settings.DEV_MODE:
        dev_user_info = CurrentUserResponse(
            user_id=settings.DEV_USER_ID,
            username=settings.DEV_USERNAME,
            real_name=settings.DEV_REAL_NAME,
            email=None,
            phone=None,
            department_id=None,
            department_name=None,
            position=None
        )

    import logging; logger = logging.getLogger(__name__); logger.info(f"DEBUG: dev_mode={settings.DEV_MODE}, type={type(settings.DEV_MODE)}")
    return ConfigResponse(
        dev_mode=settings.DEV_MODE,
        dev_user_info=dev_user_info,
        version=settings.APP_VERSION,
        app_name=settings.APP_NAME
    )
