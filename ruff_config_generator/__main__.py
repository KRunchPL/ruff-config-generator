import argparse
from enum import auto, StrEnum
from typing import cast

from .downloader import download_settings_page
from .generator import generate_toml_configuration


class Command(StrEnum):
    """
    Available script commands.
    """

    DOWNLOAD = auto()
    GENERATE = auto()


parser = argparse.ArgumentParser(
    prog='RuffConfigGenerator',
    description='Generates ruff default configuration file.',
)
parser.add_argument(
    'command',
    choices=Command,
    type=Command,
)
arguments = parser.parse_args()

match cast(Command, arguments.command):
    case Command.DOWNLOAD:
        download_settings_page()
    case Command.GENERATE:
        generate_toml_configuration()
