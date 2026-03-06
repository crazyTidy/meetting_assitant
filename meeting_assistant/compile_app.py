#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import argparse
import os

from meeting_assistant.utils import file_util


def set_environment(environment_json):
    """设置环境变量。"""
    for key, value in environment_json.items():
        key = key.upper()
        print(f"set {key}:{value}")
        os.environ[key] = f"{value}"


def check_args(args):
    """检查参数。"""
    if args.config is None:
        return

    if not os.path.exists(args.config):
        raise Exception(f"The config file {args.config} does not exist.")

    if not os.path.isfile(args.config):
        raise Exception(f"The config file {args.config} is a directory.")

    file_path = args.config
    if file_path.endswith(".json"):
        config_json = file_util.read_json(file_path)
        set_environment(config_json)

    elif file_path.endswith(".ini"):
        config_json = file_util.read_ini(file_path)
        set_environment(config_json["config"])

    elif file_path.endswith(".yaml"):
        config_json = file_util.read_yaml(file_path)
        set_environment(config_json["config"])

    else:
        raise Exception(f"The config file {args.config} must endswith json/ini/yaml.")


def run_app():
    """启动 app。"""
    # 保证环境加载设置生效
    from meeting_assistant import app

    app.main()


def main():
    parser = argparse.ArgumentParser(description="App.")
    parser.add_argument("-c", "--config", type=str, default=None, help="App config, support json/ini/yaml.")
    args = parser.parse_args()

    check_args(args)

    run_app()


if __name__ == "__main__":
    main()
