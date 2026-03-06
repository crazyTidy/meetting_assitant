#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import traceback

import pip


def pip_install_package(package_name):
    """调用 pip 安装依赖包。"""
    try:
        print(f"pip install {package_name}")
        pip.main(["install", package_name])
        return True
    except Exception as e:
        traceback.print_exc()
    return False


def do_pip_install_requirements():
    """安装依赖。"""
    fr = open("requirements.txt", "r")
    fw_installed = open("requirements-installed.txt", "w")
    fw_ignored = open("requirements-ignored.txt", "w")

    for package_name in fr.readlines():
        package_name = package_name.strip()
        flag = pip_install_package(package_name)
        # 记录已安装和未安装
        if flag:
            fw_installed.write(package_name)
            fw_installed.write("\n")
        else:
            fw_ignored.write(package_name)
            fw_ignored.write("\n")
    fr.close()
    fw_installed.close()
    fw_ignored.close()


def main():
    do_pip_install_requirements()


if __name__ == "__main__":
    main()
