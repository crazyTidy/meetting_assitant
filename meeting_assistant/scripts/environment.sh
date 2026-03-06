#!/bin/bash
# 导出环境变量脚本

echo "导出环境变量"

######## 服务配置 ########
# 服务地址
export HOST="0.0.0.0"
# 服务端口
export PORT=8888
# 服务进程数
export WORKERS=1
# 服务重启策略
export RELOAD=0
# 服务模式 http
export HTTPS=0
# 数据库
export SQLALCHEMY_DATABASE_URL="postgresql://username:password@ip:port/database_name?options=-c%20search_path=schema_name"

######## redis 配置 ########
# redis 服务地址
export REDIS_HOST="127.0.0.1"
# redis 服务端口号
export REDIS_PORT=6379
# redis 数据库
export REDIS_DB=0

######## minio 配置 ########
# minio 服务地址
export MINIO_ENDPOINT="127.0.0.1:9000"
# minio 访问 access key
export MINIO_ACCESS_KEY="admin"
# minio 访问 secret key
export MINIO_SECRET_KEY="admin"

######## session 配置 ########
# session 密钥
export SESSION_SECRET_KEY="1234567890"
# session 类型
# 0 表示使用 header cookie
# 1 表示使用 header authorization
# 2 表示使用 redis
export SESSION_TYPE=0