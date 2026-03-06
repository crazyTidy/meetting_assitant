#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import aiohttp
import requests


def http_post(url, body_json, headers):
    """发送 http post 请求。"""
    response = requests.post(url=url, json=body_json, headers=headers, verify=False, timeout=5)
    status_code = response.status_code
    headers = dict(response.headers)
    content = response.content

    return status_code, headers, content


def http_post_stream(url, body_json, headers):
    """发送 http post 请求，流式返回。"""
    response = requests.post(url=url, json=body_json, headers=headers, verify=False, stream=True, timeout=5)
    status_code = response.status_code
    headers = dict(response.headers)

    if status_code != 200:
        yield status_code, headers, response.content
    else:
        for chunk in response.iter_content(256):
            yield status_code, headers, chunk


async def async_http_post(url, body_json, headers):
    """异步发送 http post 请求。"""
    async with aiohttp.ClientSession() as client_session:
        async with client_session.post(url=url, json=body_json, headers=headers, timeout=5) as response:
            status_code = response.status
            headers = dict(response.headers)
            content = await response.read()
            return status_code, headers, content


async def async_http_post_stream(url, body_json, headers):
    """异步发送 http post 请求，流式返回。"""
    async with aiohttp.ClientSession() as client_session:
        async with client_session.post(url=url, json=body_json, headers=headers, timeout=5) as response:
            status_code = response.status
            headers = dict(response.headers)

            if status_code != 200:
                content = await response.read()
                yield status_code, headers, content
            else:
                async for chunk in response.content.iter_chunked(256):
                    yield status_code, headers, chunk


def main():
    pass


if __name__ == "__main__":
    main()
