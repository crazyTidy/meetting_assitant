#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import base64
import json
import urllib.parse


def base64_encode(data):
    """base64 编码，支持 string 和 bytes。"""
    data_base64 = base64.b64encode(data)
    return data_base64


def base64_decode(data_base64):
    """base64 解码，支持 string 和 bytes。"""
    data = base64.b64decode(data_base64)
    return data


def json_encode(data_json):
    """json 编码。"""
    data = json.dumps(data_json)
    return data


def json_decode(data):
    """json 解码。"""
    data_json = json.loads(data)
    return data_json


def url_encode(data):
    """url 编码。"""
    data_url = urllib.parse.quote(data)
    return data_url


def url_decode(data_url):
    """url 解码。"""
    data = urllib.parse.unquote(data_url)
    return data


def main():
    pass


if __name__ == "__main__":
    main()
