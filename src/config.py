import configparser
from pathlib import Path

config_path = "/config/config.ini"  # Path where default config is located

root_dir = Path(__file__).parent.parent
parser = configparser.ConfigParser().read(root_dir.joinpath(config_path))


def get(section, key):
    parser.get(section, key)


def set():
    parser.set(section, key, value)


def save():
    with open(root_dir.joinpath(config_path), "w") as file:
        parser.write(file)
