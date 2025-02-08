import requests

from .configuration import SETTINGS_HTML_FILE, VERSION_FILE


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
    """
    response = requests.get(_SETTINGS_HTML_URL, timeout=_REQUEST_TIMEOUT)
    response.raise_for_status()
    SETTINGS_HTML_FILE.write_text(response.text, encoding='utf-8')


def _download_latest_version() -> None:
    """
    Fetch letest version of ruff from PyPI and save it to file.
    """
    response = requests.get(_RUFF_PYPI_INFORMATION_URL, timeout=_REQUEST_TIMEOUT)
    response.raise_for_status()
    VERSION_FILE.write_text(response.json()['info']['version'], encoding='utf-8')
