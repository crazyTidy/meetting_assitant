#!/usr/bin/ python
# -*- encoding: utf-8 -*-
"""
Author: sys
"""
import os
import readline
import sys


class Command:

    def __init__(self):
        self.history_filepath = os.path.expanduser("~/.history")

        self.command_function = {
            "exit": self.exit,
            "quit": self.quit,
            "help": self.help,
        }

    def add_function(self, function):
        """添加执行函数。"""
        self.command_function[function.__name__] = function

    def exit(self):
        print("Goodbye! Exit.")
        sys.exit()

    def quit(self):
        print("Goodbye! Quit.")
        sys.exit()

    def help(self):
        print("Available commands:" + ", ".join(self.command_function.keys()))

    def default(self):
        print("Unknown command! Type 'help' for a list of commands.")

    def complete_text(self, text, state):
        """自动补全。"""
        options = list()
        for cmd in self.command_function.keys():
            if cmd.startswith(text):
                options.append(cmd)

        if state < len(options):
            return options[state]
        else:
            return None

    # 启用历史记录
    def load_histories(self):
        """加载历史记录"""
        if os.path.exists(self.history_filepath):
            readline.read_history_file(self.history_filepath)

        # 设置历史记录长度
        readline.set_history_length(100)

    def run(self):
        # 设置补全函数
        readline.set_completer(self.complete_text)
        # 绑定 Tab 键触发补全
        readline.parse_and_bind("tab: complete")

        self.load_histories()

        while True:
            try:
                # 获取用户输入
                command = input("Cmd> ").strip().lower()

                # 执行对应函数
                function = self.command_function.get(command, self.default)
                function()
            except KeyboardInterrupt:
                print("Use 'exit' or 'quit' to exit the program.")
            except EOFError:
                print("Goodbye!")
                break
            finally:
                # 保存历史记录
                readline.write_history_file(self.history_filepath)


def main():
    command = Command()
    command.add_function(main)
    command.run()


if __name__ == "__main__":
    main()
