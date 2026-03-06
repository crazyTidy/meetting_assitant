#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import asyncio
import logging
import traceback

from ..utils import http_util, log_util


async def test_async_http_post():
    url = "http://127.0.0.1:1089/"
    body_json = {"hello": "world"}
    status_code, headers, content = await http_util.async_http_post(url, body_json, None)
    logging.debug(f"async_http_post status_code:{status_code} headers:{headers}, content:{content}")

    async for status_code, headers, content in http_util.async_http_post_stream(url, body_json, None):
        logging.debug(f"async_http_post_stream status_code:{status_code} headers:{headers}, content:{content}")


def main():
    log_util.set_log(True)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test_async_http_post())
    except:
        logging.error(traceback.format_exc())
        loop.close()


if __name__ == "__main__":
    main()
