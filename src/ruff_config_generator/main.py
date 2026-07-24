import argparse
import sys
from enum import auto, StrEnum
from pathlib import Path
from typing import cast

from loguru import logger

from ruff_config_generator.app_config import AppConfiguration

from . import app_config
from .downloader import download
from .generator import generate_configuration


class Command(StrEnum):
    """
    Available script commands.
    """

    DOWNLOAD = auto()
    GENERATE = auto()
    BOTH = auto()


def _setup_logger() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level='INFO',
        format=(
            '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
            '<level>{level: <8}</level> | '
            '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
        ),
    )


def main() -> int:
    """
    Run the tool.

    :return: system exit code (0 for success, 1 for failure)
    """
    _setup_logger()

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
    except Exception:  # noqa: BLE001
        logger.exception('Operation failed')
        return 1
    else:
        logger.info('Operation completed successfully')
        return 0
