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
from ..utils.clients.minio_client import MinioClient


async def test_async_minio_client_list():
    bucket_name = "test"
    minio_client = MinioClient()

    # 枚举文件，包括子文件夹
    file_object_list = await minio_client.async_list_bucket_files(bucket_name=bucket_name, directory_prefix="", is_sub_directory=True)
    for object in file_object_list:
        logging.debug(f"async_list_bucket_files:{object.object_name} {object.is_dir} include sub_directory")

    # 枚举文件，不包括子文件夹
    file_object_list = await minio_client.async_list_bucket_files(bucket_name=bucket_name, directory_prefix="", is_sub_directory=False)
    for object in file_object_list:
        logging.debug(f"async_list_bucket_files:{object.object_name} {object.is_dir}")

    # 枚举文件夹，包括子文件夹
    directory_object_list = await minio_client.async_list_bucket_directories(bucket_name=bucket_name, directory_prefix="", is_sub_directory=True)
    for object in directory_object_list:
        logging.debug(f"async_list_bucket_directories:{object.object_name} {object.is_dir} include sub_directory")

    # 枚举文件夹，不包括子文件夹
    directory_object_list = await minio_client.async_list_bucket_directories(bucket_name=bucket_name, directory_prefix="", is_sub_directory=False)
    for object in directory_object_list:
        logging.debug(f"async_list_bucket_directories:{object.object_name} {object.is_dir}")


async def test_async_minio_client():
    minio_client = MinioClient()

    bucket_name = "test"
    object_name = "test.json"

    write_text_json = {"hello": "world"}
    file_path = os.path.join(directory_config.CONST_TEMP_DIRECTORY, "test_upload.json")
    await file_util.async_write_json(file_path, write_text_json)

    # 创建 bucket
    flag = await minio_client.async_create_bucket(bucket_name)
    logging.debug(f"async_create_bucket:{flag}")

    # 上传文件
    flag = await minio_client.async_upload_file(bucket_name=bucket_name, object_name=object_name, file_path=file_path)
    logging.debug(f"async_upload_file:{flag}")

    # 上传文件夹
    object_name = "json/test.json"
    flag = await minio_client.async_upload_file(bucket_name=bucket_name, object_name=object_name, file_path=file_path)
    logging.debug(f"async_upload_file:{flag}")

    # 上传文件夹
    object_name = "json/sub_json/test.json"
    flag = await minio_client.async_upload_file(bucket_name=bucket_name, object_name=object_name, file_path=file_path)
    logging.debug(f"async_upload_file:{flag}")

    await test_async_minio_client_list()

    # 下载文件
    file_path = os.path.join(directory_config.CONST_TEMP_DIRECTORY, "test_download.json")
    flag = await minio_client.async_download_file(bucket_name=bucket_name, object_name=object_name, file_path=file_path)
    logging.debug(f"async_download_file:{flag}")

    upload_url = await minio_client.async_generate_presigned_upload_url(bucket_name=bucket_name, object_name=object_name)
    logging.debug(f"async_generate_presigned_upload_url:{upload_url}")

    download_url = await minio_client.async_generate_presigned_download_url(bucket_name=bucket_name, object_name=object_name)
    logging.debug(f"async_generate_presigned_download_url:{download_url}")

    # 删除文件
    object_name = "test.json"
    flag = await minio_client.async_remove_file(bucket_name=bucket_name, object_name=object_name)
    logging.debug(f"async_remove_file:{flag}")

    object_name = "json/sub_json/test.json"
    flag = await minio_client.async_remove_file(bucket_name=bucket_name, object_name=object_name)
    logging.debug(f"async_remove_file:{flag}")

    object_name = "json/sub_json"
    flag = await minio_client.async_remove_file(bucket_name=bucket_name, object_name=object_name)
    logging.debug(f"async_remove_file:{flag}")

    await test_async_minio_client_list()


def main():
    log_util.set_log(True)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test_async_minio_client())
    except:
        logging.error(traceback.format_exc())
    loop.close()


if __name__ == "__main__":
    main()
