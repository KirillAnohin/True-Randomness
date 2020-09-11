import configparser
from pathlib import Path

config_path = "/config/config.ini"  # Path where default config is located

root_dir = Path(__file__).parent.parent
parser = configparser.ConfigParser().read(root_dir.joinpath(config_path))


def get(section, key):
    try:
        parser.get(section, key)
    except Exception as e:
        print(e)

def set(section, key, value):
    try:
        parser.set(section, key, value)
    except Exception as e:
        print(e)


def save():
    with open(root_dir.joinpath(config_path), "w") as file:
        parser.write(file)
