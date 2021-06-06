import json
import shlex
from dataclasses import asdict

from handle_curl.parse_curl import parse_curl


def rewrite(line: str) -> dict:
    list_command = shlex.split(line)
    list_command = [word.strip() for word in list_command]

    list_list_command = []  # list[list[str]]
    # 利用 ; 把一行 str 分割成不同的命令（echo、curl 等）
    pre_index = 0
    for i, element in enumerate(list_command):
        if element == ';':  # 不同命令之间分割
            list_list_command.append(list_command[pre_index: i])
            pre_index = i + 1  # 更新下个 list_command 的起始点
    list_list_command.append(list_command[pre_index:])

    print(list_list_command)
    curl = parse_curl(list_list_command[0])
    return asdict(curl)


if __name__ == "__main__":
    with open('curl.txt') as f:
        result = rewrite(f.readlines()[0])
    with open('curl.json', 'w+', encoding='utf8') as f:
        f.write(json.dumps(result, indent=4))
