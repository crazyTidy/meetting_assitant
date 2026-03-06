#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SessionMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, dispatch=None):
        super().__init__(app, dispatch)

    def load_session(self, request: Request):
        """加载 session 信息。"""
        pass

    def save_session(self, request: Request, response: Response):
        """保存 session 信息。"""
        pass

    async def dispatch(self, request, call_next):
        """基类继承，分发处理请求。"""
        # 1.加载 session 信息
        self.load_session(request)

        # 2.处理请求
        response = await call_next(request)

        # 3.保存 session 信息
        self.save_session(request, response)
        return response


def main():
    pass


if __name__ == "__main__":
    main()
