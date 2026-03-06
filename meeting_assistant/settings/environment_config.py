#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import os

# 基础配置
HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
RELOAD = int(os.environ["RELOAD"])
WORKERS = int(os.environ["WORKERS"])

# 证书配置
# 0 表示使用 http
# 1 表示开启 https 单向认证
# 2 表示开启 https 双向认证
HTTPS = int(os.environ["HTTPS"])

# 数据库配置
SQLALCHEMY_DATABASE_URL = os.environ["SQLALCHEMY_DATABASE_URL"]

######## redis 配置 ########
# redis 服务地址
REDIS_HOST = os.environ["REDIS_HOST"]
# redis 服务端口号
REDIS_PORT = os.environ["REDIS_PORT"]
# redis 数据库
REDIS_DB = os.environ["REDIS_DB"]

######## minio 配置 ########
# minio 服务地址
MINIO_ENDPOINT = os.environ["MINIO_ENDPOINT"]
# minio 访问 access key
MINIO_ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]
# minio 访问 secret key
MINIO_SECRET_KEY = os.environ["MINIO_SECRET_KEY"]

######## session 配置 ########
# session 密钥
SESSION_SECRET_KEY = os.environ["SESSION_SECRET_KEY"]
# session 类型
# 0 表示使用 header cookie
# 1 表示使用 header authorization
# 2 表示使用 redis
SESSION_TYPE = os.environ["SESSION_TYPE"]


def main():
    pass


if __name__ == "__main__":
    main()
