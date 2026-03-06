#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import logging
import time

from fastapi import Request
from fastapi.responses import JSONResponse

from .session_middleware import SessionMiddleware


class PermissionMiddleware(SessionMiddleware):
    """继承自 SessionMiddleware，实现权限检查。"""

    def __init__(self, app, dispatch=None):
        super().__init__(app, dispatch)

    async def parse_http_request(self, request: Request):
        """解析请求。"""
        interface_method = ""
        module_name = ""
        version_code = ""
        function_name = ""

        # 分割 url，删除空内容
        url_list = [u for u in request.url.path.split("/") if u != ""]
        logging.debug(f"url_list:{url_list}")

        interface_method = url_list[0]

        if url_list[1] == "polling":
            # 确保请求方法是 POST, Content-Type
            if request.method.lower() == "post" and request.headers["Content-Type"].lower() == "application/json":
                body_json = await request.json()
                module_name = body_json["parameters"]["module_name"]
                version_code = body_json["parameters"]["version_code"]
                function_name = body_json["parameters"]["function_name"]
        else:
            module_name = url_list[1]
            version_code = url_list[2]
            function_name = url_list[3]

        logging.debug(f"interface_method:{interface_method} module_name:{module_name} version_code:{version_code} function_name:{function_name}")
        return interface_method, module_name, version_code, function_name

    async def check_permission(self, request: Request):
        """根据用户登录情况，展开鉴权。"""
        interface_method, module_name, version_code, function_name = await self.parse_http_request(request)

        # 1.忽略登录接口
        if module_name == "user_managing" and (function_name == "login" or function_name == "fingerprint_login"):
            return None

        # 2.检查用户登录状态
        session_json = request.state.session_json

        # 2.1.未登录
        if session_json is None:
            logging.warning("request has no session.")
            body_json = {
                "code": 401,
                "message": "您未登录，请登录后访问。",
            }
            return JSONResponse(content=body_json, status_code=401)

        # 2.2.会话过期
        session_expiration_timestamp = session_json["session_expiration_timestamp"]
        current_timestamp = time.time()

        if session_expiration_timestamp < current_timestamp:
            logging.warning(f"request has expiry session for {session_expiration_timestamp} - {current_timestamp} = {session_expiration_timestamp - current_timestamp}.")
            body_json = {
                "code": 401,
                "message": "您登录已经失效，请重新登录后访问。",
            }
            return JSONResponse(content=body_json, status_code=401)

        # 3.已登录，检查权限
        for permission in session_json["user_permissions"]:
            if permission["module_name"] != module_name:
                continue

            # 检查无 Api 权限，禁止通过 Api 访问
            if interface_method == "api" and not permission["has_api_flag"]:
                break

            # 其它情况不限制
            return None

        body_json = {
            "code": 403,
            "message": "您没有访问该 url 的权限，请联系管理员授权。",
        }
        return JSONResponse(content=body_json, status_code=403)

    async def dispatch(self, request: Request, call_next):
        """基类继承，分发处理请求。"""
        # 1.加载 session 信息
        self.load_session(request)

        # 2.处理请求
        # 检查权限
        response = await self.check_permission(request)
        if response is None:
            response = await call_next(request)

        # 3.保存 session 信息
        self.save_session(request, response)
        return response


def main():
    pass


if __name__ == "__main__":
    main()
