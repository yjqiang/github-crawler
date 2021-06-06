import json
from typing import Any

import toml


def print_dict(data: dict) -> None:
    """
    https://stackoverflow.com/questions/12943819/how-to-prettyprint-a-json-file
    :param data:
    :return:
    """
    print(json.dumps(data, indent=4))


def toml_load(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return toml.load(f)


def save_json(path: str, data: dict) -> None:
    with open(path, 'w+', encoding='utf8') as f:
        f.write(json.dumps(data, indent=4))
