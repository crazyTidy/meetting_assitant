@REM 导出环境变量脚本
@REM 注意：windows 下环境变量不可使用 " 或者 ' 
@echo off

echo "导出环境变量"

@REM ######## 服务配置 ########
@REM 服务地址
set HOST=0.0.0.0
@REM 服务端口
set PORT=8888
@REM 服务进程数
set WORKERS=1
@REM 服务重启策略
set RELOAD=0
@REM 服务模式 http
set HTTPS=0
@REM 数据库
set SQLALCHEMY_DATABASE_URL=postgresql://username:password@ip:port/database_name?options=-c%20search_path=schema_name

@REM ######## redis 配置 ########
@REM redis 服务地址
set REDIS_HOST=127.0.0.1
@REM redis 服务端口号
set REDIS_PORT=6379
@REM redis 数据库
set REDIS_DB=0

@REM ######## minio 配置 ########
@REM minio 服务地址
set MINIO_ENDPOINT=127.0.0.1:9000
@REM minio 访问 access key
set MINIO_ACCESS_KEY=admin
@REM minio 访问 secret key
set MINIO_SECRET_KEY=admin

@REM ######## session 配置 ########
@REM session 密钥
set SESSION_SECRET_KEY=1234567890
@REM session 类型
@REM 0 表示使用 header cookie
@REM 1 表示使用 header authorization
@REM 2 表示使用 redis
set SESSION_TYPE=0