import logging
from pathlib import Path

import pytest
import requests
from pytest_mock import MockerFixture

from ruff_config_generator.downloader import (
    _download_latest_version,
    _download_settings_page,
    _REQUEST_TIMEOUT,
    _RUFF_PYPI_INFORMATION_URL,
    _SETTINGS_HTML_URL,
    download,
)


@pytest.fixture
def mock_settings_file(mocker: MockerFixture, tmp_path: Path) -> Path:
    """
    Mock SETTINGS_HTML_FILE to use temporary directory.

    :param mocker: pytest mocker fixture
    :param tmp_path: pytest temporary directory fixture
    :return: mocked settings file path
    """
    settings_file = tmp_path / 'settings.html'
    mocker.patch('ruff_config_generator.downloader.SETTINGS_HTML_FILE', settings_file)
    return settings_file


@pytest.fixture
def mock_version_file(mocker: MockerFixture, tmp_path: Path) -> Path:
    """
    Mock VERSION_FILE to use temporary directory.

    :param mocker: pytest mocker fixture
    :param tmp_path: pytest temporary directory fixture
    :return: mocked version file path
    """
    version_file = tmp_path / 'version.txt'
    mocker.patch('ruff_config_generator.downloader.VERSION_FILE', version_file)
    return version_file


def test_download_settings_page_success(
    mocker: MockerFixture,
    mock_settings_file: Path,
) -> None:
    """
    Test successful download of settings page.

    :param mocker: pytest mocker fixture
    :param mock_settings_file: mocked settings file path
    """
    mock_response = mocker.Mock()
    mock_response.text = '<html>Settings content</html>'
    mock_get = mocker.patch('requests.get', return_value=mock_response)

    _download_settings_page()

    mock_get.assert_called_once_with(_SETTINGS_HTML_URL, timeout=_REQUEST_TIMEOUT)
    mock_response.raise_for_status.assert_called_once()
    assert mock_settings_file.read_text(encoding='utf-8') == '<html>Settings content</html>'


def test_download_settings_page_request_exception(
    mocker: MockerFixture,
    mock_settings_file: Path,  # noqa: ARG001
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test handling of request exception when downloading settings page.

    :param mocker: pytest mocker fixture
    :param mock_settings_file: mocked settings file path (ensures path is mocked)
    :param caplog: pytest log capture fixture
    """
    mocker.patch('requests.get', side_effect=requests.RequestException('Network error'))

    with caplog.at_level(logging.ERROR), pytest.raises(requests.RequestException, match='Network error'):
        _download_settings_page()

    assert 'Failed to download settings page' in caplog.text


def test_download_settings_page_http_error(
    mocker: MockerFixture,
    mock_settings_file: Path,  # noqa: ARG001
) -> None:
    """
    Test handling of HTTP error when downloading settings page.

    :param mocker: pytest mocker fixture
    :param mock_settings_file: mocked settings file path (ensures path is mocked)
    """
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError('404 Not Found')
    mocker.patch('requests.get', return_value=mock_response)

    with pytest.raises(requests.HTTPError, match='404 Not Found'):
        _download_settings_page()


def test_download_latest_version_success(
    mocker: MockerFixture,
    mock_version_file: Path,
) -> None:
    """
    Test successful download of latest ruff version.

    :param mocker: pytest mocker fixture
    :param mock_version_file: mocked version file path
    """
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'info': {'version': '0.14.1'}}
    mock_get = mocker.patch('requests.get', return_value=mock_response)

    _download_latest_version()

    mock_get.assert_called_once_with(_RUFF_PYPI_INFORMATION_URL, timeout=_REQUEST_TIMEOUT)
    mock_response.raise_for_status.assert_called_once()
    assert mock_version_file.read_text(encoding='utf-8') == '0.14.1'


def test_download_latest_version_request_exception(
    mocker: MockerFixture,
    mock_version_file: Path,  # noqa: ARG001
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test handling of request exception when fetching version.

    :param mocker: pytest mocker fixture
    :param mock_version_file: mocked version file path (ensures path is mocked)
    :param caplog: pytest log capture fixture
    """
    mocker.patch('requests.get', side_effect=requests.RequestException('Network error'))

    with caplog.at_level(logging.ERROR), pytest.raises(requests.RequestException, match='Network error'):
        _download_latest_version()

    assert 'Failed to fetch ruff version from PyPI' in caplog.text


def test_download_latest_version_key_error(
    mocker: MockerFixture,
    mock_version_file: Path,  # noqa: ARG001
    caplog: pytest.LogCaptureFixture,
) -> None:
    """
    Test handling of unexpected PyPI response format.

    :param mocker: pytest mocker fixture
    :param mock_version_file: mocked version file path (ensures path is mocked)
    :param caplog: pytest log capture fixture
    """
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'unexpected': 'format'}
    mocker.patch('requests.get', return_value=mock_response)

    with caplog.at_level(logging.ERROR), pytest.raises(KeyError):
        _download_latest_version()

    assert 'Unexpected PyPI response format' in caplog.text


def test_download_both_operations(
    mocker: MockerFixture,
    mock_settings_file: Path,  # noqa: ARG001
    mock_version_file: Path,  # noqa: ARG001
) -> None:
    """
    Test that download() calls both download operations.

    :param mocker: pytest mocker fixture
    :param mock_settings_file: mocked settings file path (ensures path is mocked)
    :param mock_version_file: mocked version file path (ensures path is mocked)
    """
    mock_download_settings = mocker.patch('ruff_config_generator.downloader._download_settings_page')
    mock_download_version = mocker.patch('ruff_config_generator.downloader._download_latest_version')

    download()

    mock_download_settings.assert_called_once()
    mock_download_version.assert_called_once()
