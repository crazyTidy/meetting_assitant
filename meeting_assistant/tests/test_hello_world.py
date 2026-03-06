#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
from fastapi.testclient import TestClient

from ..app import app


# 测试删除不存在的条目
def test_get_hello_world():
    test_client = TestClient(app)

    response = test_client.get(url="/")
    print("response.text:", response.text)

    assert response.status_code == 200
    assert response.text == '"Hello World!"'


def test_post_hello_world():
    test_client = TestClient(app)

    response = test_client.post(
        url="/",
        json={"username": "hello", "password": "world"},
    )
    print("response.text:", response.text)

    assert response.status_code == 200
    content_json = response.json()
    assert content_json == {"username": "hello", "password": "world"}


def main():
    test_get_hello_world()
    test_post_hello_world()


if __name__ == "__main__":
    main()
