#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import json
import os
import shutil
import sys

from Cython.Build import cythonize
from setuptools import setup
from setuptools.command.build_ext import build_ext


def absolute_directory(file):
    """获取文件夹全路径。"""
    file = os.path.abspath(file)
    if os.path.isfile(file):
        file = os.path.dirname(file)
    return os.path.normpath(file)


def base_directory(file):
    """获取文件夹名称。"""
    return os.path.basename(absolute_directory(file))


IGNORE_PYTHON_LIST = [
    "compile_app.py",
    "compile_tool.py",
    "cython_setup.py",
    "pip_requirements.py",
    "pyinstaller_setup.py",
    "requirements.py",
]
PACKAGE_NAME = base_directory(__file__)
print(f"PACKAGE_NAME:{PACKAGE_NAME}")


def list_files(directory, is_full_path=False, is_sub_directory=False):
    """获取目录下的文件。"""
    file_list = []

    if os.path.isfile(directory):
        print(f"{directory} should be a directory, not a file.")
        return file_list

    if not os.path.exists(directory):
        print(f"{directory} is not exist.")
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


class CustomBuildExt(build_ext):
    """自定义构建命令，避免编译时包含平台信息。"""

    def build_linux_extension(self, extension):
        """linux 使用 gcc，添加 gcc 编译优化命令。"""
        # 启用最高级别的优化
        extension.extra_compile_args.append("-O3")
        # 显示所有警告信息
        extension.extra_compile_args.append("-Wall")
        # 禁用未使用的函数警告
        extension.extra_compile_args.append("-Wno-unused-function")
        # 生成位置无关代码
        extension.extra_compile_args.append("-fPIC")
        # 在函数中使用堆栈保护，以防止堆栈溢出攻击
        extension.extra_compile_args.append("-fstack-protector-all")
        # 去除函数调用栈的帧指针
        extension.extra_compile_args.append("-fomit-frame-pointer")

        # 去除链接时的调试信息
        extension.extra_link_args.append("-s")
        # 确保所有动态链接的库在加载时立即进行绑定（而非延迟绑定）
        extension.extra_link_args.append("-Wl,-z,now")
        # 将堆栈标记为不可执行，进一步增强内存保护
        extension.extra_link_args.append("-Wl,-z,noexecstack")

    def build_windows_extension(self, extension):
        """windows 使用 cl，添加 cl 编译优化命令。"""
        # 启用最高级别的优化
        extension.extra_compile_args.append("-O3")
        # 显示所有警告信息
        extension.extra_compile_args.append("-Wall")
        # 禁用未使用的函数警告
        # extension.extra_compile_args.append("-Wno-unused-function")
        # 生成位置无关代码
        extension.extra_compile_args.append("-fPIC")
        # 在函数中使用堆栈保护，以防止堆栈溢出攻击
        extension.extra_compile_args.append("-fstack-protector-all")
        # 去除函数调用栈的帧指针
        extension.extra_compile_args.append("-fomit-frame-pointer")

        # 去除链接时的调试信息
        extension.extra_link_args.append("-s")
        # 确保所有动态链接的库在加载时立即进行绑定（而非延迟绑定）
        extension.extra_link_args.append("-Wl,-z,now")
        # 将堆栈标记为不可执行，进一步增强内存保护
        extension.extra_link_args.append("-Wl,-z,noexecstack")

    def build_extensions(self):
        """构建编译命令。"""
        for extension in self.extensions:
            if sys.platform.startswith("linux"):
                self.build_linux_extension(extension)
            elif sys.platform.startswith("win"):
                self.build_windows_extension(extension)
            else:
                raise Exception(f"unknow platform {sys.platform}")

        super().build_extensions()

    def get_ext_filename(self, full_name):
        """构建编译后文件名。"""
        # 获取默认的扩展文件名
        full_name = super().get_ext_filename(full_name)

        # 移除平台特定信息
        # linux 平台：xxx.cpython-38-x86_64-linux-gnu.so
        # windows 平台：xxx.cp313-win_amd64.pyd
        full_name_splits = full_name.split(".")
        assert len(full_name_splits) == 3
        full_name = f"{full_name_splits[0]}.{full_name_splits[2]}"
        return full_name

    def copy_extensions_to_source(self):
        """编译完成，拷贝编译结果至指定目录。"""
        global PACKAGE_NAME

        # 删除 xxx.c 文件
        source_file_list = self.get_source_files()
        for source_file in source_file_list:
            if os.path.exists(source_file):
                os.remove(source_file)

        # 处理 __init__.py 文件，将其拷贝至 build 目录
        current_directory = absolute_directory(__file__)
        build_py = self.get_finalized_command("build_py")

        import_list_dict = dict()
        import_list_dict["default"] = []
        for extension in self.extensions:
            # 判断平台
            if sys.platform.startswith("linux"):
                ends = ".so"
            elif sys.platform.startswith("win"):
                ends = ".pyd"
            else:
                raise Exception(f"unknow platform {sys.platform}")

            # inplace_file 编译的源文件
            # regular_file 目的文件
            inplace_file, regular_file = self._get_inplace_equivalent(build_py, extension)

            if regular_file.endswith(f"__init__{ends}"):
                # 重组源文件目录
                inplace_file = inplace_file.replace(ends, ".py")
                inplace_file = os.path.join(current_directory, "..", inplace_file)

                # 重组目标文件目录
                regular_file = regular_file.replace(ends, ".py")
                regular_file = os.path.join(current_directory, regular_file)

                # 执行拷贝
                shutil.copy(inplace_file, regular_file)

            else:
                # 添加编译的模块
                # linux 目录使用 /
                # windows 目录使用 \
                import_list_dict["default"].append(inplace_file.replace(ends, "").replace("/", ".").replace("\\", "."))

                # 记录隐藏的 import
                # 重组源文件目录
                inplace_file = inplace_file.replace(ends, ".py")
                inplace_file = os.path.join(current_directory, "..", inplace_file)

                import_list_dict[inplace_file] = parse_imports(inplace_file)

        # 保存隐藏 import
        hidden_imports_file_path = os.path.join(current_directory, "builds", "hidden_imports.json")
        fw = open(hidden_imports_file_path, "w", encoding="utf-8")
        fw.write(json.dumps(import_list_dict, indent=4))
        fw.close()

        # 禁止拷贝，请勿解除注释
        # super().copy_extensions_to_source()


def list_pythons():
    """枚举目录中的 py 文件。"""
    global IGNORE_PYTHON_LIST

    python_list = []
    current_directory = absolute_directory(__file__)

    # 删除 build 目录缓存
    build_directory = os.path.join(current_directory, "builds")
    if os.path.exists(build_directory):
        print(f"delete build directory:{build_directory}.")
        shutil.rmtree(build_directory)

    # 枚举
    for file_path in list_files(directory=current_directory, is_full_path=True, is_sub_directory=True):
        if file_path.endswith(".py"):
            # 忽略指定文件
            file_directory, file_name = os.path.split(file_path)
            if file_name in IGNORE_PYTHON_LIST:
                continue

            print(f"find .py:{file_path}.")
            python_list.append(file_path)

    print(f"total:{len(python_list)}")
    return python_list


def cython_setup():
    """执行 cython 编译。"""
    global PACKAGE_NAME

    # 枚举所有 py 文件
    python_list = list_pythons()

    # 编译所有 py 文件
    setup(
        name=PACKAGE_NAME,  # 模块名称
        ext_modules=cythonize(
            python_list,
            nthreads=os.cpu_count(),
        ),  # 待编译 python 文件列表
        script_args=[
            "build_ext",
            "--inplace",
            f"--parallel={os.cpu_count()}",
        ],  # 保证 build 运行后，会执行 copy_extensions_to_source
        options={
            "build_ext": {
                "build_temp": "builds",  # build 临时目录
                "build_lib": "builds",  # build 保存目录
            },
        },
        cmdclass={
            "build_ext": CustomBuildExt,  # build 执行类
        },
    )


def main():
    cython_setup()


if __name__ == "__main__":
    main()
