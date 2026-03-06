#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
from redis import Redis

from ...settings import environment_config


class RedisClient:
    """单例模式。"""

    redis_client_instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.redis_client_instance:
            cls.redis_client_instance = super().__new__(cls, *args, **kwargs)
        return cls.redis_client_instance

    def __init__(self):
        self.redis_client = Redis(host=environment_config.REDIS_HOST, port=environment_config.REDIS_PORT, db=environment_config.REDIS_DB)

    def dict_set(self, key, value):
        """字典存储键值对。"""
        self.redis_client.set(key, value)

    def dict_get(self, key):
        """字典查询键。"""
        return self.redis_client.get(key)

    def dict_delete(self, key):
        """字典删除键。"""
        self.redis_client.delete(key)

    def list_append(self, key, value):
        """列表增加元素。"""
        self.redis_client.rpush(key, value)

    def list_length(self, key):
        """列表长度。"""
        return self.redis_client.llen(key)

    def list_index(self, key, index):
        """列表获取元素。"""
        return self.redis_client.lindex(key, index)

    def list_list(self, key):
        return self.redis_client.lrange(key, 0, -1)

    def list_delete(self, key, value):
        """列表删除元素。"""
        self.redis_client.lrem(key, 0, value)

    def list_empty(self, key):
        """列表清空。"""
        self.redis_client.delete(key)

    def set_add(self, key, value):
        """集合添加元素。"""
        self.redis_client.sadd(key, value)

    def set_length(self, key):
        """集合长度。"""
        return self.redis_client.scard(key)

    def set_remove(self, key, value):
        """集合删除元素"""
        self.redis_client.srem(key, value)

    def set_clear(self, key):
        """集合清空元素"""
        self.redis_client.delete(key)

    def set_set(self, key):
        """获取所有元素。"""
        return self.redis_client.smembers(key)


def main():
    pass


if __name__ == "__main__":
    main()
