import argparse
from enum import auto, StrEnum
from typing import cast

from .downloader import download
from .generator import generate_configuration


class Command(StrEnum):
    """
    Available script commands.
    """

    DOWNLOAD = auto()
    GENERATE = auto()
    BOTH = auto()


def main() -> int:
    """
    Run the tool.

    :return: system exit code
    """
    parser = argparse.ArgumentParser(
        prog='RuffConfigGenerator',
        description='Generates ruff default configuration file.',
    )
    parser.add_argument(
        'command',
        choices=Command,
        type=Command,
        nargs='?',
        default=Command.BOTH,
    )
    arguments = parser.parse_args()

    match cast(Command, arguments.command):
        case Command.DOWNLOAD:
            download()
        case Command.GENERATE:
            generate_configuration()
        case Command.BOTH:
            download()
            generate_configuration()
    return 0
