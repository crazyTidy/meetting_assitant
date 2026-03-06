"""Token演示接口"""
from fastapi import APIRouter, Request, Header, HTTPException, status, Query
from typing import Optional
from ..utils.jwt_util import generate_test_token, decode_token

router = APIRouter()


@router.get("/demo/tokens")
async def get_demo_tokens():
    """
    获取演示用的测试 Token。

    返回两个不同用户的 Token，用于测试用户隔离功能。
    """
    # Token 1: 研发部 - 张三
    token1 = generate_test_token(
        user_id="user-001",
        username="zhangsan",
        real_name="张三",
        department_id="dept-001",
        department_name="研发部",
        position="高级工程师"
    )

    # Token 2: 市场部 - 李四
    token2 = generate_test_token(
        user_id="user-002",
        username="lisi",
        real_name="李四",
        department_id="dept-002",
        department_name="市场部",
        position="市场经理"
    )

    return {
        "users": [
            {
                "id": "user-001",
                "name": "张三",
                "department": "研发部",
                "position": "高级工程师",
                "token": token1
            },
            {
                "id": "user-002",
                "name": "李四",
                "department": "市场部",
                "position": "市场经理",
                "token": token2
            }
        ],
        "usage": {
            "header": "Authorization: Bearer <token>",
            "url": "?token=<token>",
            "examples": [
                "curl -H 'Authorization: Bearer <token>' http://localhost:7654/api/v1/users/me",
                "curl http://localhost:7654/api/v1/users/me?token=<token>",
                "浏览器直接访问: http://localhost:7654/api/v1/users/me?token=<token>"
            ]
        }
    }


@router.get("/demo/parse-token")
async def parse_token(
    request: Request,
    token: Optional[str] = None
):
    """
    解析当前请求中的 Token 并显示用户信息。

    支持通过 Header 或 URL 参数传递 Token。
    """
    # Try to get token from multiple sources
    if not token:
        token = request.query_params.get("token")
        token = request.query_params.get("Token")

    if not token:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "缺少 Token",
                "usage": "请通过以下方式传递 Token:",
                "methods": [
                    "URL 参数: ?token=<token>",
                    "Header: Authorization: Bearer <token>"
                ],
                "example_url": f"{request.url.scheme}://{request.url.netloc}{request.url.path}?token=your-token-here"
            }
        )

    try:
        payload = decode_token(token)
        return {
            "valid": True,
            "user_info": {
                "user_id": payload.get("sub"),
                "username": payload.get("username"),
                "real_name": payload.get("real_name"),
                "department_id": payload.get("department_id"),
                "department_name": payload.get("department_name"),
                "position": payload.get("position"),
            },
            "token_info": {
                "issued_at": payload.get("iat"),
                "expires_at": payload.get("exp")
            },
            "next_steps": {
                "use_in_browser": f"在浏览器中直接访问: ?token={token[:50]}...",
                "user_meeting_list": f"{request.url.scheme}://{request.url.netloc}/api/v1/meetings/?token={token[:50]}..."
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": str(e)}
        )


@router.post("/demo/switch-user")
async def switch_user(
    token: str,
    request: Request
):
    """
    切换当前用户（演示用）。

    前端可以使用这个接口来模拟切换不同用户。
    """
    try:
        payload = decode_token(token)
        return {
            "success": True,
            "message": f"已切换到用户: {payload.get('real_name', payload.get('sub'))}",
            "user_info": {
                "user_id": payload.get("sub"),
                "username": payload.get("username"),
                "real_name": payload.get("real_name"),
                "department": payload.get("department_name")
            },
            "next_step": {
                "use_this_token": "在后续请求中使用此 Token",
                "browser_url": f"{request.url.scheme}://{request.url.netloc}/api/v1/users/me?token={token[:50]}..."
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": str(e)}
        )
