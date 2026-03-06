#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import asyncio
import logging
import os
import traceback

from ..settings import directory_config
from ..utils import file_util, log_util


async def test_async_read_write_json():
    write_text_json = {
        "hello": "world",
    }

    file_name = "test_text_json.json"
    file_path = os.path.join(directory_config.CONST_TEMP_DIRECTORY, file_name)
    await file_util.async_write_json(file_path, write_text_json)

    read_text_json = await file_util.async_read_json(file_path)
    logging.debug(f"async_read_json:{read_text_json}")


async def test_read_write_ini():
    write_text_json = {
        "config": {
            "hello": "world",
        },
    }

    file_name = "test_text_json.ini"
    file_path = os.path.join(directory_config.CONST_TEMP_DIRECTORY, file_name)
    file_util.write_ini(file_path, write_text_json)

    read_text_json = file_util.read_ini(file_path)
    logging.debug(f"read_ini:{read_text_json}")


async def test_read_write_yaml():
    write_text_json = {
        "config": {
            "hello": "world",
        },
    }

    file_name = "test_text_json.yaml"
    file_path = os.path.join(directory_config.CONST_TEMP_DIRECTORY, file_name)
    file_util.write_yaml(file_path, write_text_json)

    read_text_json = file_util.read_yaml(file_path)
    logging.debug(f"read_yaml:{read_text_json}")


def main():
    log_util.set_log(True)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test_async_read_write_json())
        loop.run_until_complete(test_read_write_ini())
        loop.run_until_complete(test_read_write_yaml())
    except:
        logging.error(traceback.format_exc())
        loop.close()


if __name__ == "__main__":
    main()
