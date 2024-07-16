import json
import os


current_path = os.path.abspath(__file__)
static_path = os.path.join(os.path.dirname(current_path), "resource", "static")


def read_config():
    config = {}
    with open(os.path.join(static_path, "privateConfig.json")) as json_file:
        config = json.load(json_file)
    return config


def write_config(config):
    with open(os.path.join(static_path, "privateConfig.json"), 'w') as json_file:
        json_file.write(json.dumps(config, indent=2, ensure_ascii=False))
