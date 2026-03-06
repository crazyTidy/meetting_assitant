#!/bin/bash
# 结束进程脚本

################################ 基本变量 开始 ################################
# 获取执行脚本绝对路径
ABSOLUTE_SCRIPT_PATH=$(realpath "$0")
echo "ABSOLUTE_SCRIPT_PATH:$ABSOLUTE_SCRIPT_PATH"
# 获取执行脚本绝对目录
ABSOLUTE_SCRIPT_DIRECTORY=$(dirname "$ABSOLUTE_SCRIPT_PATH")
echo "ABSOLUTE_SCRIPT_DIRECTORY:$ABSOLUTE_SCRIPT_DIRECTORY"
# 获取执行脚本文件名
SCRIPT_NAME=$(basename "$ABSOLUTE_SCRIPT_PATH")
echo "SCRIPT_NAME:$SCRIPT_NAME"
# 获取执行脚本上级目录，即工程目录
ABSOLUTE_SCRIPT_PARENT_DIRECTORY=$(realpath "$ABSOLUTE_SCRIPT_DIRECTORY/..")
echo "ABSOLUTE_SCRIPT_PARENT_DIRECTORY:$ABSOLUTE_SCRIPT_PARENT_DIRECTORY"
# 获取执行脚本上上级目录
ABSOLUTE_SCRIPT_PARENT_PARENT_DIRECTORY=$(realpath "$ABSOLUTE_SCRIPT_PARENT_DIRECTORY/..")
echo "ABSOLUTE_SCRIPT_PARENT_PARENT_DIRECTORY:$ABSOLUTE_SCRIPT_PARENT_PARENT_DIRECTORY"
# 获取执行脚本上级目录名，即包名
PACKAGE_NAME=$(basename "$ABSOLUTE_SCRIPT_PARENT_DIRECTORY")
echo "PACKAGE_NAME:$PACKAGE_NAME"

# 进入执行脚本上级目录，即工程目录
cd "$ABSOLUTE_SCRIPT_PARENT_DIRECTORY"
################################ 基本变量 结束 ################################


################################ 用户自定义功能 开始 ################################
# 查找进程 id
PID=$(pgrep -f "$PACKAGE_NAME.app" | xargs)

# 检查是否找到了进程
if [ -n "$PID" ]; then
    echo "找到进程 $PACKAGE_NAME 的 PID:$PID，并停止"
    # 结束进程
    kill -9 $PID
else
    echo "未找到进程 $PACKAGE_NAME"
fi
################################ 用户自定义功能 结束 ################################