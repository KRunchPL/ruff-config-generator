from pathlib import Path

import pytest
import requests
from logot import logged, Logot
from logot.loguru import LoguruCapturer
from pytest_mock import MockerFixture

from ruff_config_generator.app_config import AppConfiguration
from ruff_config_generator.downloader import (
    _download_latest_version,
    _download_page,
    _REQUEST_TIMEOUT,
    _RUFF_PYPI_INFORMATION_URL,
    _SETTINGS_HTML_URL,
    download,
)


@pytest.fixture
def app_config(tmp_path: Path) -> AppConfiguration:
    return AppConfiguration(
        workdir=tmp_path,
        settings_html_file_name='settings.html',
        rules_html_file_name='rules.html',
        version_file_name='version.txt',
        default_values_file_name='temp',
        adjusted_values_file_name='temp',
        overrides={},
    )


def test_download_page_success(
    mocker: MockerFixture,
    app_config: AppConfiguration,
) -> None:
    mock_response = mocker.Mock()
    mock_response.text = '<html>Settings content</html>'
    mock_get = mocker.patch('requests.get', return_value=mock_response)

    _download_page(_SETTINGS_HTML_URL, app_config.settings_html_file, 'settings')

    mock_get.assert_called_once_with(_SETTINGS_HTML_URL, timeout=_REQUEST_TIMEOUT)
    mock_response.raise_for_status.assert_called_once()
    assert app_config.settings_html_file.read_text(encoding='utf-8') == '<html>Settings content</html>'


def test_download_page_request_exception(
    mocker: MockerFixture,
    app_config: AppConfiguration,
) -> None:
    mocker.patch('requests.get', side_effect=requests.RequestException('Network error'))

    with Logot(capturer=LoguruCapturer).capturing() as logot:
        with pytest.raises(requests.RequestException, match='Network error'):
            _download_page(_SETTINGS_HTML_URL, app_config.settings_html_file, 'settings')
        logot.assert_logged(logged.error('Failed to download settings page'))


def test_download_page_http_error(
    mocker: MockerFixture,
    app_config: AppConfiguration,
) -> None:
    mock_response = mocker.Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError('404 Not Found')
    mocker.patch('requests.get', return_value=mock_response)

    with pytest.raises(requests.HTTPError, match='404 Not Found'):
        _download_page(_SETTINGS_HTML_URL, app_config.settings_html_file, 'settings')


def test_download_latest_version_success(
    mocker: MockerFixture,
    app_config: AppConfiguration,
) -> None:
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'info': {'version': '0.14.1'}}
    mock_get = mocker.patch('requests.get', return_value=mock_response)

    _download_latest_version(app_config)

    mock_get.assert_called_once_with(_RUFF_PYPI_INFORMATION_URL, timeout=_REQUEST_TIMEOUT)
    mock_response.raise_for_status.assert_called_once()
    assert app_config.version_file.read_text(encoding='utf-8') == '0.14.1'


def test_download_latest_version_request_exception(
    mocker: MockerFixture,
    app_config: AppConfiguration,
) -> None:
    mocker.patch('requests.get', side_effect=requests.RequestException('Network error'))

    with Logot(capturer=LoguruCapturer).capturing() as logot:
        with pytest.raises(requests.RequestException, match='Network error'):
            _download_latest_version(app_config)
        logot.assert_logged(logged.error('Failed to fetch ruff version from PyPI'))


def test_download_latest_version_key_error(
    mocker: MockerFixture,
    app_config: AppConfiguration,
) -> None:
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'unexpected': 'format'}
    mocker.patch('requests.get', return_value=mock_response)

    with Logot(capturer=LoguruCapturer).capturing() as logot:
        with pytest.raises(KeyError):
            _download_latest_version(app_config)
        logot.assert_logged(logged.error('Unexpected PyPI response format'))


def test_download_both_operations(
    mocker: MockerFixture,
    app_config: AppConfiguration,
) -> None:
    mock_download_page = mocker.patch('ruff_config_generator.downloader._download_page')
    mock_download_version = mocker.patch('ruff_config_generator.downloader._download_latest_version')

    download(app_config)

    assert mock_download_page.call_count == 2
    mock_download_version.assert_called_once()
