import logging

import requests

from .configuration import SETTINGS_HTML_FILE, VERSION_FILE


logger = logging.getLogger(__name__)


_SETTINGS_HTML_URL = 'https://docs.astral.sh/ruff/settings/'
_RUFF_PYPI_INFORMATION_URL = 'https://pypi.org/pypi/ruff/json'
_REQUEST_TIMEOUT = 10  # in seconds


def download() -> None:
    """
    Download ruff's settings page and version of PyPI.
    """
    _download_settings_page()
    _download_latest_version()


def _download_settings_page() -> None:
    """
    Download ruff's settings page as HTML.

    :raises requests.RequestException: if download fails
    """
    logger.info('Downloading settings page from %s', _SETTINGS_HTML_URL)
    try:
        response = requests.get(_SETTINGS_HTML_URL, timeout=_REQUEST_TIMEOUT)
        response.raise_for_status()
        SETTINGS_HTML_FILE.write_text(response.text, encoding='utf-8')
        logger.info('Settings page saved to %s', SETTINGS_HTML_FILE)
    except requests.RequestException:
        logger.exception('Failed to download settings page')
        raise


def _download_latest_version() -> None:
    """
    Fetch latest version of ruff from PyPI and save it to file.

    :raises requests.RequestException: if download fails
    :raises KeyError: if PyPI response format is unexpected
    """
    logger.info('Fetching latest ruff version from PyPI')
    try:
        response = requests.get(_RUFF_PYPI_INFORMATION_URL, timeout=_REQUEST_TIMEOUT)
        response.raise_for_status()
        version = response.json()['info']['version']
        VERSION_FILE.write_text(version, encoding='utf-8')
        logger.info('Ruff version %s saved to %s', version, VERSION_FILE)
    except requests.RequestException:
        logger.exception('Failed to fetch ruff version from PyPI')
        raise
    except KeyError:
        logger.exception('Unexpected PyPI response format')
        raise
