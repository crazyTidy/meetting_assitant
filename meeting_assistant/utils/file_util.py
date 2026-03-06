#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import json
import logging
import os
from configparser import ConfigParser

import aiofiles
import yaml


def read_bytes(file_path):
    """以字节形式读取文件。"""
    fr = open(file_path, "rb")
    content = fr.read()
    return content


async def async_read_bytes(file_path):
    """以字节形式异步读取文件。"""
    async with aiofiles.open(file_path, "rb") as fr:
        content = await fr.read()
        return content


def write_bytes(file_path, content):
    """以字节形式写入文件。"""
    fw = open(file_path, "wb")
    fw.write(content)


async def async_write_bytes(file_path, content):
    """以字节形式异步写入文件。"""
    async with aiofiles.open(file_path, "wb") as fw:
        await fw.write(content)


def read_string(file_path, encoding="utf-8"):
    """以字符串形式读取文件。"""
    content = read_bytes(file_path)
    text = content.decode(encoding)
    return text


async def async_read_string(file_path, encoding="utf-8"):
    """以字符串形式异步读取文件。"""
    content = await async_read_bytes(file_path)
    text = content.decode(encoding)
    return text


def write_string(file_path, text, encoding="utf-8"):
    """以字符串形式写入文件。"""
    content = text.encode(encoding)
    write_bytes(file_path, content)


async def async_write_string(file_path, text, encoding="utf-8"):
    """以字符串形式异步写入文件。"""
    content = text.encode(encoding)
    await async_write_bytes(file_path, content)


def read_json(file_path, encoding="utf-8"):
    """读取 json 文件。"""
    text = read_string(file_path, encoding)
    text_json = json.loads(text)
    return text_json


async def async_read_json(file_path, encoding="utf-8"):
    """异步读取 json 文件。"""
    text = await async_read_string(file_path, encoding)
    text_json = json.loads(text)
    return text_json


def write_json(file_path, text_json, encoding="utf-8"):
    """写入 json 文件。"""
    text = json.dumps(text_json)
    write_string(file_path, text, encoding)


async def async_write_json(file_path, text_json, encoding="utf-8"):
    """异步写入 json 文件。"""
    text = json.dumps(text_json)
    await async_write_string(file_path, text, encoding)


def read_ini(file_path, encoding="utf-8"):
    """读取 ini 文件。"""
    config_parser = ConfigParser()
    text = read_string(file_path, encoding)
    config_parser.read_string(text)

    text_json = dict()
    for section in config_parser.sections():
        text_json[section] = dict(config_parser.items(section))

    return text_json


async def async_read_ini(file_path, encoding="utf-8"):
    """读取 ini 文件。"""
    config_parser = ConfigParser()
    text = await async_read_string(file_path, encoding)
    config_parser.read_string(text)

    text_json = dict()
    for section in config_parser.sections():
        text_json[section] = dict(config_parser.items(section))

    return text_json


def write_ini(file_path, text_json, encoding="utf-8"):
    """写入 ini 文件。"""
    config_parser = ConfigParser()
    for section, options in text_json.items():
        config_parser[section] = options

    # 保存更改到文件
    fw = open(file_path, "w", encoding=encoding)
    config_parser.write(fw)
    fw.close()


def read_yaml(file_path, encoding="utf-8"):
    """读取 yaml 文件。"""
    fr = open(file_path, "r", encoding=encoding)
    text_json = yaml.safe_load(fr)
    return text_json


def write_yaml(file_path, text_json, encoding="utf-8"):
    """写入 yaml 文件。"""
    fw = open(file_path, "w", encoding=encoding)
    yaml.safe_dump(text_json, fw)


def absolute_directory(file):
    """获取文件夹全路径。"""
    file = os.path.abspath(file)
    if os.path.isfile(file):
        file = os.path.dirname(file)
    return os.path.normpath(file)


def base_directory(file):
    """获取文件夹名称。"""
    return os.path.basename(absolute_directory(file))


def list_files(directory, is_full_path=False, is_sub_directory=False):
    """获取目录下的文件。"""
    file_list = []

    if os.path.isfile(directory):
        logging.warning(f"{directory} should be a directory, not a file.")
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


def main():
    pass


if __name__ == "__main__":
    main()
