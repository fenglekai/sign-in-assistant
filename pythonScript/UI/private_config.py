import json
import os
import shutil
from use_path import config_path, default_config_path


def read_config():
    if os.path.exists(config_path) == False:
        shutil.copy(default_config_path, config_path)
    config = {}
    with open(config_path) as json_file:
        config = json.load(json_file)
    return config


def write_config(config):
    with open(config_path, 'w') as json_file:
        json_file.write(json.dumps(config, indent=2, ensure_ascii=False))
