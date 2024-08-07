import os


current_path = os.path.abspath(__file__)
local_path = os.path.dirname(current_path)
static_path = os.path.join(local_path, "resource", "static")
default_config_path = os.path.join(static_path, "defaultConfig.json")
config_path = os.path.join(static_path, "privateConfig.json")