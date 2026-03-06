"""Security utility functions."""
from fastapi import Request, HTTPException, status
from typing import Optional, Dict, Any


def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user information from request.state."""
    return getattr(request.state, "user", None)


def require_auth(request: Request) -> Dict[str, Any]:
    """Get current user information and raise exception if not authenticated."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user
