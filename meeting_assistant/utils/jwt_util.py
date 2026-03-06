"""JWT Token generation utility."""
import jwt
from datetime import datetime, timedelta
from ..settings.config import settings


def generate_test_token(
    user_id: str,
    username: str = None,
    real_name: str = None,
    department_id: str = None,
    department_name: str = None,
    position: str = None,
    expires_in_days: int = 365
) -> str:
    """Generate test JWT Token."""
    payload = {
        "sub": user_id,
        "username": username,
        "real_name": real_name,
        "department_id": department_id,
        "department_name": department_name,
        "position": position,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=expires_in_days)
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def validate_token(token: str) -> dict | None:
    """Validate and parse JWT Token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if "sub" in payload:
            payload["user_id"] = payload["sub"]
        return payload
    except:
        return None


def decode_token(token: str) -> dict:
    """Decode JWT Token."""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
