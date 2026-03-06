#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import os

from . import directory_config

# https 证书配置
# server 的私钥
CONST_SERVER_PRIVATE_KEY = os.path.join(directory_config.CONST_STATIC_CERTIFICATE_DIRECTORY, "server.pem")
# server 的证书
CONST_SERVER_CERTIFICATE = os.path.join(directory_config.CONST_STATIC_CERTIFICATE_DIRECTORY, "server.crt")
# ca 的证书
CONST_CA_CERTIFICATE = os.path.join(directory_config.CONST_STATIC_CERTIFICATE_DIRECTORY, "ca.crt")


def main():
    pass


if __name__ == "__main__":
    main()
