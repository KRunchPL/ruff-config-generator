import argparse
import logging
from enum import auto, StrEnum
from pathlib import Path
from typing import cast

from ruff_config_generator.app_config import AppConfiguration

from . import app_config
from .downloader import download
from .generator import generate_configuration


logger = logging.getLogger(__name__)


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

    :return: system exit code (0 for success, 1 for failure)
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

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
    parser.add_argument(
        '-c',
        '--config',
        type=Path,
        required=False,
    )
    arguments = parser.parse_args()

    if arguments.config:
        app_config.set_app_config(AppConfiguration(toml_file=arguments.config))  # type: ignore [call-arg]
    try:
        match cast('Command', arguments.command):
            case Command.DOWNLOAD:
                download()
            case Command.GENERATE:
                generate_configuration()
            case Command.BOTH:
                download()
                generate_configuration()
    except Exception:
        logger.exception('Operation failed')
        return 1
    else:
        logger.info('Operation completed successfully')
        return 0
