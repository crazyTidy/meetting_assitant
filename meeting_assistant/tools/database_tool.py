#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import os

from sqlalchemy import create_engine

from ..models.base_model import BaseModel
from ..settings import directory_config
from ..utils import log_util, module_util
from .command_tool import Command

database_filename = "template.db"


def find_and_load_models():
    model_package = f"{__package__}..models"
    model_directory = os.path.join(directory_config.CONST_PROJECT_DIRECTORY, "models")

    def filter_function(root, filename):
        # 忽略非 py 文件
        if not filename.endswith(".py"):
            return False

        # 忽略不以 _model.py 命名的文件
        if not filename.endswith("_model.py"):
            print(f"ignore {filename}")
            return False

        print(f"import {filename}")
        return True

    module_util.find_and_import_module(
        model_package,
        model_directory,
        filter_function=filter_function,
        is_sub_directory=True,
    )


def get_all_tables():
    """获取所有表名称。"""
    table_list = []
    for table in BaseModel.metadata.tables:
        table_list.append(table)
    return table_list


def show_tables():
    """显示所有表。"""
    table_list = get_all_tables()
    print(f"tables:{','.join(table_list)}")


def create_tables():
    """创建数据库表。"""
    sqlalchemy_database_url = f"sqlite:///{directory_config.CONST_TEMP_DIRECTORY}/{database_filename}"
    print(f"sqlalchemy_database_url:{sqlalchemy_database_url}")

    engine = create_engine(sqlalchemy_database_url)

    table_list = get_all_tables()
    print(f"create tables:{','.join(table_list)}")

    BaseModel.metadata.create_all(engine, checkfirst=True)


def drop_tables():
    """删除数据库表。"""
    sqlalchemy_database_url = f"sqlite:///{directory_config.CONST_TEMP_DIRECTORY}/{database_filename}"
    print(f"sqlalchemy_database_url:{sqlalchemy_database_url}")
    engine = create_engine(sqlalchemy_database_url)

    table_list = get_all_tables()
    print(f"drop tables:{','.join(table_list)}")
    BaseModel.metadata.drop_all(engine, checkfirst=True)


def main():
    log_util.set_log(True)

    command = Command()
    command.add_function(find_and_load_models)
    command.add_function(create_tables)
    command.add_function(drop_tables)
    command.add_function(show_tables)
    command.run()


if __name__ == "__main__":
    main()
