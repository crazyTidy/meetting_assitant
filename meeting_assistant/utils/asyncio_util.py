#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor


def asyncio_to_thread(sync_function, *args, **kwargs):
    """实现 asyncio.to_thread() 用于支撑 python 3.7 以下版本。"""
    loop = asyncio.get_running_loop()

    def wrapper():
        return sync_function(*args, **kwargs)

    return loop.run_in_executor(ThreadPoolExecutor(), wrapper)


def main():
    pass


if __name__ == "__main__":
    main()
