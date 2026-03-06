#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import importlib
import importlib.metadata
import importlib.util
import os
import traceback

import pkg_resources


def absolute_directory(file):
    """获取文件夹全路径。"""
    file = os.path.abspath(file)
    if os.path.isfile(file):
        file = os.path.dirname(file)
    return os.path.normpath(file)


def base_directory(file):
    """获取文件夹名称。"""
    return os.path.basename(absolute_directory(file))


def import_to_pip_package(imp):
    """import 查询 pip 包。"""
    imp = imp.split(".")[0]
    try:
        distribution = pkg_resources.get_distribution(imp)
        return distribution.project_name
    except Exception as e:
        print(f"pkg_resources can't find package for {imp}")

    try:
        # 导入模块
        module = importlib.import_module(imp)
        # 根据模块路径，判断系统模块
        spec = importlib.util.find_spec(imp)
        if "\\site-packages\\" in spec.origin or "\\Lib\\" in spec.origin:
            return None
    except Exception as e:
        print(f"importlib can't import module {imp}")

    return None


def parse_imports(python_file_path):
    """解析 py 文件，获取 import 列表。"""
    fr = open(python_file_path, "r", encoding="utf-8")

    import_set = set()
    for line in fr.readlines():
        # 解析 import xxx
        if line.startswith("import ") or line.startswith("from "):
            imp = line.split(" ")[1].strip()

            if imp.startswith("."):
                continue

            import_set.add(imp)

    if "" in import_set:
        import_set.remove("")

    import_list = list(import_set)
    return import_list


def list_files(directory, is_full_path=False, is_sub_directory=False):
    """获取目录下的文件。"""
    file_list = []

    if os.path.isfile(directory):
        print(f"{directory} should be a directory, not a file.")
        return file_list

    for name in os.listdir(directory):
        full_name = os.path.join(directory, name)
        if os.path.isfile(full_name):
            if is_full_path:
                file_list.append(full_name)
            else:
                file_list.append(name)
        else:
            if is_sub_directory:
                file_list += list_files(full_name, is_full_path=is_full_path, is_sub_directory=is_sub_directory)

    return file_list


def list_pythons():
    """枚举目录中的 py 文件。"""
    python_list = []
    current_directory = absolute_directory(__file__)

    # 枚举
    for file_path in list_files(directory=current_directory, is_full_path=True, is_sub_directory=True):
        if file_path.endswith(".py"):

            print(f"find .py:{file_path}.")
            python_list.append(file_path)

    print(f"total:{len(python_list)}")
    return python_list


def do_build_requirements():
    """构建项目依赖包。"""

    # 枚举所有 py 文件
    python_list = list_pythons()

    # 解析所有 py 文件，获取 import
    import_list = []
    for file_path in python_list:
        import_list += parse_imports(file_path)

    # 查询 pip 包
    import_set = set(import_list)
    pip_package_list = []
    for imp in import_set:
        pip_package = import_to_pip_package(imp)
        if pip_package != None:
            pip_package_list.append(pip_package.lower())

    # 保存文件
    fw = open("requirements.txt", "w")
    for pkg in sorted(set(pip_package_list), reverse=False):
        fw.write(pkg)
        fw.write("\n")
    fw.close()


def main():
    do_build_requirements()


if __name__ == "__main__":
    main()
