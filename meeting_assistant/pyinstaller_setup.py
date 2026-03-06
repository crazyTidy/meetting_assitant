#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import json
import os
import shutil

import PyInstaller.__main__
import PyInstaller.config


def absolute_directory(file):
    """获取文件夹全路径。"""
    file = os.path.abspath(file)
    if os.path.isfile(file):
        file = os.path.dirname(file)
    return os.path.normpath(file)


def base_directory(file):
    """获取文件夹名称。"""
    return os.path.basename(absolute_directory(file))


def list_directories(directory, is_full_path=False, is_sub_directory=False):
    """获取目录下的文件夹。"""
    directory_list = []

    if os.path.isfile(directory):
        print(f"{directory} should be a directory, not a file.")
        return directory_list

    if not os.path.exists(directory):
        print(f"{directory} is not exist.")
        return directory_list

    for name in os.listdir(directory):
        full_name = os.path.join(directory, name)
        if os.path.isdir(full_name):
            if is_full_path:
                directory_list.append(full_name)
            else:
                directory_list.append(name)
        else:
            if is_sub_directory:
                directory_list += list_directories(full_name, is_full_path=is_full_path, is_sub_directory=is_sub_directory)

    return directory_list


# 获取文件本级目录
CURRENT_DIRECTORY = absolute_directory(__file__)
print(f"CURRENT_DIRECTORY:{CURRENT_DIRECTORY}")

# 获取上层目录
SCRIPT_PARENT_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "..")
print(f"SCRIPT_PARENT_DIRECTORY:{SCRIPT_PARENT_DIRECTORY}")

# 根据上层目录获取模块名
PACKAGE_NAME = base_directory(SCRIPT_PARENT_DIRECTORY)
print(f"PACKAGE_NAME:{PACKAGE_NAME}")

# 待打包的数据目录
DATA_DIRECTORY_LIST = ["statics", "logs", "temps"]


def load_hiddenimports():
    """加载 cpython 中编译的 python 文件的 import。"""
    current_directory = absolute_directory(__file__)

    # 读取 json 文件
    hidden_imports_file_path = os.path.join(current_directory, "hidden_imports.json")
    fr = open(hidden_imports_file_path, "r", encoding="utf-8")
    import_list_dict = json.loads(fr.read())
    fr.close()

    import_set = set()
    for file_path, import_list in import_list_dict.items():
        for imp in import_list:
            print(f"import {imp}")
            import_set.add(imp)

    hiddenimports = list(import_set)
    return hiddenimports


def copy_datas():
    """拷贝数据目录。"""
    global DATA_DIRECTORY_LIST
    global SCRIPT_PARENT_DIRECTORY
    global CURRENT_DIRECTORY
    global PACKAGE_NAME

    args = []

    # 拷贝本模块目录
    for data in DATA_DIRECTORY_LIST:
        # 源路径
        src = f"{SCRIPT_PARENT_DIRECTORY}/{data}/"
        # 编译路径
        dst = f"{CURRENT_DIRECTORY}/{PACKAGE_NAME}/{data}/"
        # 打包路径
        vir = f"{PACKAGE_NAME}/{data}/"

        # 检查源目录是否存在
        if not os.path.exists(src):
            print(f"{src} is not exist.")
            continue

        # 拷贝源目录至编译目录
        shutil.copytree(src, dst, dirs_exist_ok=True)

        # 增加编译命令
        args.append("--add-data")
        args.append(
            f"{dst}:{vir}",
        )

    # 拷贝子模块目录
    for sub_module_directory in list_directories(f"{SCRIPT_PARENT_DIRECTORY}/modules/", is_full_path=True, is_sub_directory=False):
        sub_module_package_name = base_directory(sub_module_directory)

        for data in DATA_DIRECTORY_LIST:
            # 源路径
            src = f"{SCRIPT_PARENT_DIRECTORY}/modules/{sub_module_package_name}/{data}/"
            # 编译路径
            dst = f"{CURRENT_DIRECTORY}/{PACKAGE_NAME}/modules/{sub_module_package_name}/{data}/"
            # 打包路径
            vir = f"{PACKAGE_NAME}/modules/{sub_module_package_name}/{data}/"

            # 检查源目录是否存在
            if not os.path.exists(src):
                print(f"{src} is not exist.")
                continue

            # 拷贝源目录至编译目录
            shutil.copytree(src, dst, dirs_exist_ok=True)

            # 增加编译命令
            args.append("--add-data")
            args.append(
                f"{dst}:{vir}",
            )

    return args


def pyinstaller_setup_app():
    """pyinstaller 编译 app。"""
    # 隐藏 import
    PyInstaller.config.CONF["hiddenimports"] = load_hiddenimports()

    # 拷贝数据目录
    data_args = copy_datas()

    # 编译 app
    args = data_args + [
        "--onefile",
        f"--name={PACKAGE_NAME}_app",
        "--distpath",
        f"{CURRENT_DIRECTORY}/pyinstaller_dist",
        "--workpath",
        f"{CURRENT_DIRECTORY}/pyinstaller_build",
        "compile_app.py",
    ]
    print(f"args:{args}")

    PyInstaller.__main__.run(args)


def pyinstaller_setup_tool():
    """pyinstaller 编译。"""
    # 隐藏 import
    PyInstaller.config.CONF["hiddenimports"] = load_hiddenimports()

    # 拷贝数据目录
    data_args = copy_datas()

    # 编译 tool
    args = data_args + [
        "--onefile",
        f"--name={PACKAGE_NAME}_tool",
        "--distpath",
        f"{CURRENT_DIRECTORY}/pyinstaller_dist",
        "--workpath",
        f"{CURRENT_DIRECTORY}/pyinstaller_build",
        "compile_tool.py",
    ]
    print(f"args:{args}")

    PyInstaller.__main__.run(args)


def main():
    pyinstaller_setup_app()
    pyinstaller_setup_tool()


if __name__ == "__main__":
    main()
