import json


def print_dict(data: dict) -> None:
    """
    https://stackoverflow.com/questions/12943819/how-to-prettyprint-a-json-file
    :param data:
    :return:
    """
    print(json.dumps(data, indent=4))
