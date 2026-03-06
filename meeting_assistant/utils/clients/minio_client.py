#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import logging
import os
import traceback
from datetime import timedelta

from minio import Minio

from ...settings import environment_config
from .. import asyncio_util


class MinioClient:
    """单例模式。"""

    minio_client_instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.minio_client_instance:
            cls.minio_client_instance = super().__new__(cls, *args, **kwargs)
        return cls.minio_client_instance

    def __init__(self):
        self.minio_client = Minio(endpoint=environment_config.MINIO_ENDPOINT, access_key=environment_config.MINIO_ACCESS_KEY, secret_key=environment_config.MINIO_SECRET_KEY, secure=False)

    def list_buckets(self):
        """枚举桶。"""
        try:
            response = self.minio_client.list_buckets()
            return response.buckets
        except Exception as e:
            logging.error(traceback.format_exc())
        return []

    async def async_list_buckets(self):
        """异步枚举桶。"""
        return await asyncio_util.asyncio_to_thread(self.list_buckets)

    def list_bucket_directories(self, bucket_name, directory_prefix=None, is_sub_directory=False):
        """枚举桶中文件夹。"""
        directories_list = []
        try:
            objects = self.minio_client.list_objects(bucket_name=bucket_name, prefix=directory_prefix, recursive=False)
            for object in objects:
                if object.is_dir:
                    directories_list.append(object)

                    if is_sub_directory:
                        sub_directory_prefix = os.path.join(directory_prefix, object.object_name)
                        logging.debug(f"list_bucket_directories sub_directory_prefix:{sub_directory_prefix}")
                        directories_list += self.list_bucket_directories(bucket_name, sub_directory_prefix, is_sub_directory)
        except Exception as e:
            logging.error(traceback.format_exc())

        return directories_list

    async def async_list_bucket_directories(self, bucket_name, directory_prefix=None, is_sub_directory=False):
        """异步枚举桶中文件夹。"""
        return await asyncio_util.asyncio_to_thread(self.list_bucket_directories, bucket_name, directory_prefix, is_sub_directory)

    def list_bucket_files(self, bucket_name, directory_prefix=None, is_sub_directory=False):
        """异步枚举桶中文件。"""
        file_list = []
        try:
            objects = self.minio_client.list_objects(bucket_name=bucket_name, prefix=directory_prefix, recursive=False)
            for object in objects:
                if object.is_dir:
                    if is_sub_directory:
                        sub_directory_prefix = os.path.join(directory_prefix, object.object_name)
                        logging.debug(f"list_bucket_files sub_directory_prefix:{sub_directory_prefix}")
                        file_list += self.list_bucket_files(bucket_name, sub_directory_prefix, is_sub_directory)
                else:
                    file_list.append(object)
        except Exception as e:
            logging.error(traceback.format_exc())

        return file_list

    async def async_list_bucket_files(self, bucket_name, directory_prefix=None, is_sub_directory=False):
        """异步枚举桶中文件。"""
        return await asyncio_util.asyncio_to_thread(self.list_bucket_files, bucket_name, directory_prefix, is_sub_directory)

    def create_bucket(self, bucket_name):
        """创建桶。"""
        # TODO 增加 bucket 重复判断
        try:
            self.minio_client.make_bucket(bucket_name=bucket_name)
            return True
        except Exception as e:
            logging.error(traceback.format_exc())
        return False

    async def async_create_bucket(self, bucket_name):
        """异步创建桶。"""
        return await asyncio_util.asyncio_to_thread(self.create_bucket, bucket_name)

    def upload_file(self, bucket_name, object_name, file_path):
        """上传文件。"""
        try:
            if object_name is None:
                object_name = os.path.basename(file_path)

            self.minio_client.fput_object(bucket_name=bucket_name, object_name=object_name, file_path=file_path)
            return True
        except Exception as e:
            logging.error(traceback.format_exc())
        return False

    async def async_upload_file(self, bucket_name, object_name, file_path):
        """异步上传文件。"""
        return await asyncio_util.asyncio_to_thread(self.upload_file, bucket_name, object_name, file_path)

    def download_file(self, bucket_name, object_name, file_path):
        """下载文件。"""
        try:
            self.minio_client.fget_object(bucket_name=bucket_name, object_name=object_name, file_path=file_path)
            return True
        except Exception as e:
            logging.error(traceback.format_exc())
        return False

    async def async_download_file(self, bucket_name, object_name, file_path):
        """异步下载文件。"""
        return await asyncio_util.asyncio_to_thread(self.download_file, bucket_name, object_name, file_path)

    def generate_presigned_upload_url(self, bucket_name, object_name, expiration_seconds=60 * 60):
        """生成预签名上传文件 url 地址。"""
        try:
            url = self.minio_client.presigned_put_object(bucket_name=bucket_name, object_name=object_name, expires=timedelta(seconds=expiration_seconds))
            return url
        except Exception as e:
            logging.error(traceback.format_exc())
            return False

    async def async_generate_presigned_upload_url(self, bucket_name, object_name, expiration_seconds=60 * 60):
        """异步生成预签名上传文件 url 地址。"""
        return await asyncio_util.asyncio_to_thread(self.generate_presigned_upload_url, bucket_name, object_name, expiration_seconds)

    def generate_presigned_download_url(self, bucket_name, object_name, expiration_seconds=60 * 60):
        """生成预签名下载文件 url 地址。"""
        try:
            url = self.minio_client.presigned_get_object(bucket_name=bucket_name, object_name=object_name, expires=timedelta(seconds=expiration_seconds))
            return url
        except Exception as e:
            logging.error(traceback.format_exc())
            return False

    async def async_generate_presigned_download_url(self, bucket_name, object_name, expiration_seconds=60 * 60):
        """异步生成预签名下载文件 url 地址。"""
        return await asyncio_util.asyncio_to_thread(self.generate_presigned_download_url, bucket_name, object_name, expiration_seconds)

    def remove_file(self, bucket_name, object_name):
        """删除文件。"""
        try:
            self.minio_client.remove_object(bucket_name, object_name)
            return True
        except Exception as e:
            logging.error(traceback.format_exc())
        return False

    async def async_remove_file(self, bucket_name, object_name):
        """异步删除文件。"""
        return await asyncio_util.asyncio_to_thread(self.remove_file, bucket_name, object_name)


def main():
    pass


if __name__ == "__main__":
    main()
