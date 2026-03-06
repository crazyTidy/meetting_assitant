"""JWT authentication middleware."""
from fastapi import Request, HTTPException, status
from jose import jwt, JWTError

from ..settings.config import settings


PUBLIC_PATHS = {
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/demo/tokens",
    "/api/v1/users/login",
    "/api/v1/users/config"
}

PUBLIC_PATH_PREFIXES = {
    "/api/v1/meetings",
}


async def auth_middleware(request: Request, call_next):
    """JWT authentication middleware."""

    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)

    for prefix in PUBLIC_PATH_PREFIXES:
        if request.url.path.startswith(prefix):
            return await call_next(request)

    if request.method == "OPTIONS":
        return await call_next(request)

    token = None
    authorization = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    if not token:
        token = request.query_params.get("token") or request.query_params.get("Token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Missing token",
                "usage": "Pass token via either Header or URL parameter",
                "header": "Authorization: Bearer <token>",
                "url": "?token=<token>"
            }
        )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing user_id")

        user_info = {
            "user_id": user_id,
            "username": payload.get("username"),
            "real_name": payload.get("real_name"),
            "email": payload.get("email"),
            "phone": payload.get("phone"),
            "department_id": payload.get("department_id"),
            "department_name": payload.get("department_name"),
            "position": payload.get("position")
        }
        request.state.user = user_info
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")

    return await call_next(request)
