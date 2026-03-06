#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import logging
import os

# 设置文件目录
CONST_SETTING_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
logging.debug(f"CONST_CURRENT_DIRECTORY:{CONST_SETTING_DIRECTORY}")

# 项目根目录
CONST_PROJECT_DIRECTORY = os.path.abspath(os.path.join(CONST_SETTING_DIRECTORY, "../"))
logging.debug(f"CONST_PROJECT_DIRECTORY:{CONST_PROJECT_DIRECTORY}")

# 静态文件目录
CONST_STATIC_DIRECTORY = os.path.abspath(os.path.join(CONST_PROJECT_DIRECTORY, "statics"))
logging.debug(f"CONST_STATIC_DIRECTORY:{CONST_STATIC_DIRECTORY}")

# 静态证书文件目录
CONST_STATIC_CERTIFICATE_DIRECTORY = os.path.abspath(os.path.join(CONST_STATIC_DIRECTORY, "certificates"))
logging.debug(f"CONST_STATIC_CERTIFICATE_DIRECTORY:{CONST_STATIC_CERTIFICATE_DIRECTORY}")

# 模板文件目录
CONST_TEMPLATE_DIRECTORY = os.path.abspath(os.path.join(CONST_PROJECT_DIRECTORY, "templates"))
logging.debug(f"CONST_TEMPLATE_DIRECTORY:{CONST_TEMPLATE_DIRECTORY}")

# 缓存文件目录
CONST_TEMP_DIRECTORY = os.path.abspath(os.path.join(CONST_PROJECT_DIRECTORY, "temps"))
logging.debug(f"CONST_TEMP_DIRECTORY:{CONST_TEMP_DIRECTORY}")


def main():
    pass


if __name__ == "__main__":
    main()
