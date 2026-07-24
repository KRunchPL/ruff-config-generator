import sys
from pathlib import Path

import typer
from loguru import logger
from typer_config import use_multifile_config

from ruff_config_generator.app_config import AppConfiguration
from ruff_config_generator.downloader import download
from ruff_config_generator.generator import generate_configuration


app = typer.Typer()


_DEFAULT_CONFIG = (Path(__file__).parent / 'default_config.toml').absolute()


def _setup_logger() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        level='INFO',
        format=(
            '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
            '<level>{level: <8}</level> | '
            '<level>{message}</level>'
        ),
    )


@app.command()
@use_multifile_config(default_files=[str(_DEFAULT_CONFIG)])
def _(ctx: typer.Context) -> None:
    config = AppConfiguration.model_validate(ctx.default_map)
    _setup_logger()
    download(config)
    generate_configuration(config)


if __name__ == '__main__':
    app()
