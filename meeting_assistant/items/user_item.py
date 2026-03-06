"""User item schemas."""
from typing import Optional
from pydantic import BaseModel


class CurrentUserResponse(BaseModel):
    """Schema for current authenticated user."""
    user_id: str
    username: Optional[str] = None
    real_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    position: Optional[str] = None


class UserInfo(BaseModel):
    """Schema for user information."""
    id: str
    username: Optional[str] = None
    real_name: Optional[str] = None
    department_name: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    token: Optional[str] = None
    dev_mode: Optional[bool] = False


class LoginResponse(BaseModel):
    """Schema for login response."""
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    user: Optional[CurrentUserResponse] = None


class ConfigResponse(BaseModel):
    """Schema for app config response."""
    dev_mode: bool
    dev_user_info: Optional[CurrentUserResponse] = None
    version: Optional[str] = None
    app_name: Optional[str] = None
