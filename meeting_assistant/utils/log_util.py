#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import logging


def set_log(debug, is_log_file=False, log_file_name="log.log"):
    """设置日志。"""

    # 获取 root logger
    logger = logging.getLogger()
    # 清除 root logger 的 handler
    logger.handlers.clear()

    formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(filename)s][%(lineno)d] %(message)s")

    if is_log_file:
        file_handler = logging.FileHandler(log_file_name)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logging.info("debug:{}".format(debug))


def main():
    pass


if __name__ == "__main__":
    main()
