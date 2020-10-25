import configparser
from configparser import NoSectionError, NoOptionError
from ast import literal_eval
from pathlib import Path


class config:
    def __init__(self):
        self.config_path = "./config/config.ini"  # Path where default config is located
        self.root_dir = Path(__file__).parent.parent
        self.parser = configparser.ConfigParser()
        self.parser.read(self.root_dir.joinpath(self.config_path))

    def get(self, section, key, default=None):
        try:
            return literal_eval(self.parser.get(section, key))
        except NoSectionError:
            return default
        except NoOptionError:
            return default

    def set(self, section, key, value):
        try:
            self.parser.set(section, key, repr(value))
        except NoSectionError:
            self.parser.add_section(section)
            self.parser.set(section, key, repr(value))

    def checkSection(self, section, default=None):
        try:
            return self.parser.has_section(section)
        except NoSectionError:
            return default

    def save(self):
        with open(self.root_dir.joinpath(self.config_path), "w") as file:
            self.parser.write(file)
