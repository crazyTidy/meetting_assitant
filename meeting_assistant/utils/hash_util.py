#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import hashlib


def sha256_hexdigest(content):
    """计算 sha 256 哈希值。"""
    sha256 = hashlib.sha256()
    sha256.update(content)
    hex_text = sha256.hexdigest()
    return hex_text


def main():
    pass


if __name__ == "__main__":
    main()
