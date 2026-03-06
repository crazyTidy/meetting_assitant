#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import logging

from ..settings import environment_config
from ..utils import jwt_util, log_util


def test_jwt():
    payload = {"data": "data"}

    token = jwt_util.jwt_encode(environment_config.SESSION_SECRET_KEY, payload)
    logging.debug(f"token:{token}")

    decoded_payload = jwt_util.jwt_decode(environment_config.SESSION_SECRET_KEY, token)
    logging.debug(f"decoded_payload:{decoded_payload}")


def main():
    log_util.set_log(True)

    test_jwt()


if __name__ == "__main__":
    main()
