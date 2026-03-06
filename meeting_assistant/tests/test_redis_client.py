#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import logging

from ..utils import log_util
from ..utils.clients.redis_client import RedisClient


def test_redis_client_dict():
    """测试 redis dict 功能。"""
    redis_client = RedisClient()

    # 测试 dict
    key = "dict"
    redis_client.dict_set(key, "1")
    value = redis_client.dict_get(key)
    logging.debug(f"dict_get:{value}.")

    redis_client.dict_set(key, 2)
    value = redis_client.dict_get(key)
    logging.debug(f"dict_get:{value}.")

    redis_client.dict_delete(key)

    value = redis_client.dict_get(key)
    logging.debug(f"dict_get:{value} after delete.")


def test_redis_client_list():
    """测试 redis list 功能。"""
    redis_client = RedisClient()

    # 测试 list
    key = "list"
    redis_client.list_append(key, "1")
    value = redis_client.list_index(key, -1)
    logging.debug(f"list_append:{value}.")

    redis_client.list_append(key, 2)
    value = redis_client.list_index(key, -1)
    logging.debug(f"list_append:{value}.")

    length = redis_client.list_length(key)
    logging.debug(f"list_length:{length}.")

    values = redis_client.list_list(key)
    logging.debug(f"list_list:{values}.")

    redis_client.list_delete(key, 2)
    length = redis_client.list_length(key)
    logging.debug(f"list_length:{length} after delete 2.")

    redis_client.list_empty(key)
    length = redis_client.list_length(key)
    logging.debug(f"list_length:{length} after empty.")


def test_redis_client_set():
    redis_client = RedisClient()

    # 测试 set
    key = "set"

    redis_client.set_add(key, "1")
    values = redis_client.set_set(key)
    logging.debug(f"set_add:{values}.")

    redis_client.set_add(key, 2)
    values = redis_client.set_set(key)
    logging.debug(f"set_add:{values}.")

    length = redis_client.set_length(key)
    logging.debug(f"set_length:{length}.")

    redis_client.set_remove(key, 2)
    length = redis_client.set_length(key)
    logging.debug(f"set_remove:{length} after remove 2.")

    redis_client.set_clear(key)
    length = redis_client.set_length(key)
    logging.debug(f"set_length:{length} after clear.")


def main():
    log_util.set_log(True)
    test_redis_client_dict()
    test_redis_client_list()
    test_redis_client_set()


if __name__ == "__main__":
    main()
