@REM 结束进程脚本
@echo off
setlocal enabledelayedexpansion

@REM ################################ 基本变量 开始 ################################
@REM 获取执行脚本绝对路径
set ABSOLUTE_SCRIPT_PATH=%~f0
echo "ABSOLUTE_SCRIPT_PATH:%ABSOLUTE_SCRIPT_PATH%"
@REM 获取执行脚本绝对目录
set ABSOLUTE_SCRIPT_DIRECTORY=%~dp0
echo "ABSOLUTE_SCRIPT_DIRECTORY:%ABSOLUTE_SCRIPT_DIRECTORY%"
@REM 获取执行脚本文件名
set SCRIPT_NAME=%~nx0
echo "SCRIPT_NAME:%SCRIPT_NAME%"
@REM 获取执行脚本上级目录
for %%i in ("%ABSOLUTE_SCRIPT_DIRECTORY%\.") do (
    set ABSOLUTE_SCRIPT_PARENT_DIRECTORY=%%~dpi
)
echo "ABSOLUTE_SCRIPT_PARENT_DIRECTORY:%ABSOLUTE_SCRIPT_PARENT_DIRECTORY%"
@REM 获取执行脚本上上级目录
for %%i in ("%ABSOLUTE_SCRIPT_PARENT_DIRECTORY%\.") do (
    set ABSOLUTE_SCRIPT_PARENT_PARENT_DIRECTORY=%%~dpi
)
echo "ABSOLUTE_SCRIPT_PARENT_PARENT_DIRECTORY:%ABSOLUTE_SCRIPT_PARENT_PARENT_DIRECTORY%"
@REM 获取执行脚本上上级目录名，即包名
@REM :~0,-1 去除末尾反斜杠 \
@REM :\=" " 按反斜杠分割路径，并用双引号包裹，不然空格 for 会报错
@REM ~ 去除双引号
set TEMP=%ABSOLUTE_SCRIPT_PARENT_DIRECTORY:~0,-1%
for %%i in ("%TEMP:\=" "%") do (
    set PACKAGE_NAME=%%~i
)
echo "PACKAGE_NAME:%PACKAGE_NAME%"

@REM 进入执行脚本上级目录，即工程目录
cd "%ABSOLUTE_SCRIPT_PARENT_DIRECTORY%"
@REM ################################ 基本变量 结束 ################################


@REM ################################ 用户自定义功能 开始 ################################
@REM 查找进程 id，并停止
wmic process where (name="python.exe" and commandline like "%%%PACKAGE_NAME%.app%%") get commandline, processid
for /f "usebackq skip=1 tokens=1 delims= " %%i in (`wmic process where "name='python.exe' and commandline like '%%%%PACKAGE_NAME%%.app%%'" get processid`) do (
    set "PID=%%i"
    echo "进程 %PACKAGE_NAME% 的 PID:!PID!"
    taskkill /pid !PID! /f
)
@REM ################################ 用户自定义功能 结束 ################################

@REM 返回执行脚本目录
cd "%ABSOLUTE_SCRIPT_DIRECTORY%"