#!/bin/bash
# 代码编译脚本

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
######## 编译为 pyd 或者 so ########
# 执行 cython 编译
python cython_setup.py

# ######## 编译执行文件 ########
# 进入编译目录
cd "$ABSOLUTE_SCRIPT_PARENT_DIRECTORY/builds"

# 执行拷贝脚本
# 注意 cp 通配符展开必须去除 "
cp $ABSOLUTE_SCRIPT_PARENT_DIRECTORY/compile*.py "$ABSOLUTE_SCRIPT_PARENT_DIRECTORY/builds/"
cp "$ABSOLUTE_SCRIPT_PARENT_DIRECTORY/pyinstaller_setup.py" "$ABSOLUTE_SCRIPT_PARENT_DIRECTORY/builds/"

# 执行 pyinstaller 编译
python pyinstaller_setup.py
################################ 用户自定义功能 结束 ################################