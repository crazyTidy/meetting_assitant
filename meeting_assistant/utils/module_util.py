#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import importlib
import logging
import os
import traceback


def find_and_import_module(directory_package, directory, filter_function, is_sub_directory=False):
    """查找指定目录，并加载模块。"""
    logging.debug(f"directory_package:{directory_package} directory:{directory}")

    module_list = []

    if os.path.isfile(directory):
        logging.warning(f"{directory} should be a directory, not a file.")
        return module_list

    # 去除 .. 或者 ...
    directory_package_list = []
    for package in directory_package.split("."):
        if package == "":
            directory_package_list = directory_package_list[:-1]
            continue

        directory_package_list.append(package)
    directory_package = ".".join(directory_package_list)

    for root, directories, files in os.walk(directory):
        # root 所指的是当前正在遍历的这个文件夹的本身的地址
        # directories 是一个 list，内容是该文件夹中所有的目录的名字（不包括子目录）
        # files 同样是 list，内容是该文件夹中所有的文件（不包括子目录）
        for filename in files:
            if not filter_function(root, filename):
                continue

            try:
                package = f"{directory_package}.{filename.rstrip('.py')}"

                logging.debug(f"import package:{package}")
                module = importlib.import_module(package)
                module_list.append(module)
            except:
                logging.error(traceback.format_exc())

        if is_sub_directory:
            # 遍历子目录，并加载模块
            for sub_directory in directories:
                sub_directory_package = f"{directory_package}.{sub_directory}"
                sub_directory = os.path.join(directory, sub_directory)
                module_list += find_and_import_module(
                    sub_directory_package,
                    sub_directory,
                    filter_function=filter_function,
                    is_sub_directory=is_sub_directory,
                )

    return module_list


def main():
    pass


if __name__ == "__main__":
    main()
