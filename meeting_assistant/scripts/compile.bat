@REM 代码编译脚本
@echo off

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
@REM ######## 编译为 pyd 或者 so ########
@REM 执行 cython 编译
python cython_setup.py

@REM ######## 编译为二进制执行文件 ########
@REM 进入编译目录
cd "%ABSOLUTE_SCRIPT_PARENT_DIRECTORY%/builds"

@REM 执行拷贝脚本
@REM 注意 copy 命令只能使用 \
copy "%ABSOLUTE_SCRIPT_PARENT_DIRECTORY%\compile_*.py" "%ABSOLUTE_SCRIPT_PARENT_DIRECTORY%\builds\"
copy "%ABSOLUTE_SCRIPT_PARENT_DIRECTORY%\pyinstaller_setup.py" "%ABSOLUTE_SCRIPT_PARENT_DIRECTORY%\builds\pyinstaller_setup.py"

@REM 执行 pyinstaller 编译
python pyinstaller_setup.py

@REM ################################ 用户自定义功能 结束 ################################

@REM 返回执行脚本目录
cd "%ABSOLUTE_SCRIPT_DIRECTORY%"