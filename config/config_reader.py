from configparser import ConfigParser
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.ini"

_parser = ConfigParser()
if not _parser.read(CONFIG_FILE):
    raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")


def get_str(section: str, key: str) -> str:
    return _parser.get(section, key)


def get_int(section: str, key: str) -> int:
    return _parser.getint(section, key)


def get_bool(section: str, key: str) -> bool:
    return _parser.getboolean(section, key)