from pathlib import Path

import requests
from loguru import logger

from .app_config import AppConfiguration


_RULES_HTML_URL = 'https://docs.astral.sh/ruff/rules/'
_SETTINGS_HTML_URL = 'https://docs.astral.sh/ruff/settings/'
_RUFF_PYPI_INFORMATION_URL = 'https://pypi.org/pypi/ruff/json'
_REQUEST_TIMEOUT = 10  # in seconds


def download(app_config: AppConfiguration) -> None:
    """
    Download ruff's settings page and version of PyPI.

    :param app_config: application configuration
    """
    _download_page(_SETTINGS_HTML_URL, app_config.settings_html_file, 'settings')
    _download_page(_RULES_HTML_URL, app_config.rules_html_file, 'rules')
    _download_latest_version(app_config)


def _download_page(url: str, output_file: Path, name: str) -> None:
    """
    Download ruff's configuration page as HTML.

    :param url: page url
    :param output_file: file to save downloaded page to
    :param name: human friendly name of the downloaded page
    """
    logger.info('Downloading {} page from {}', name, url)
    try:
        response = requests.get(url, timeout=_REQUEST_TIMEOUT)
        response.raise_for_status()
        output_file.write_text(response.text, encoding='utf-8')
        logger.info('Page with {} saved to {}', name, output_file)
    except requests.RequestException:
        logger.exception('Failed to download {} page', name)
        raise


def _download_latest_version(app_config: AppConfiguration) -> None:
    """
    Fetch latest version of ruff from PyPI and save it to file.

    :param app_config: application configuration
    """
    logger.info('Fetching latest ruff version from PyPI')
    try:
        response = requests.get(_RUFF_PYPI_INFORMATION_URL, timeout=_REQUEST_TIMEOUT)
        response.raise_for_status()
        version = response.json()['info']['version']
        app_config.version_file.write_text(version, encoding='utf-8')
        logger.info('Ruff version {} saved to {}', version, app_config.version_file)
    except requests.RequestException:
        logger.exception('Failed to fetch ruff version from PyPI')
        raise
    except KeyError:
        logger.exception('Unexpected PyPI response format')
        raise
