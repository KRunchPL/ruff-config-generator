import pytest
from logot import logged, Logot
from logot.loguru import LoguruCapturer
from pytest_mock import MockerFixture

from ruff_config_generator.main import Command, main


@pytest.fixture(autouse=True)
def mock_setup_logger(mocker: MockerFixture) -> None:
    mocker.patch('ruff_config_generator.main._setup_logger')


def test_command_enum_values() -> None:
    """Test Command enum has expected values."""
    assert Command.DOWNLOAD == 'download'  # type: ignore [comparison-overlap]
    assert Command.GENERATE == 'generate'  # type: ignore [comparison-overlap]
    assert Command.BOTH == 'both'  # type: ignore [comparison-overlap]


@pytest.mark.parametrize(
    ['args', 'expected_command'],
    [
        ([], Command.BOTH),
        (['download'], Command.DOWNLOAD),
        (['generate'], Command.GENERATE),
        (['both'], Command.BOTH),
    ],
)
def test_main_command_parsing(
    mocker: MockerFixture,
    args: list[str],
    expected_command: Command,
) -> None:
    """
    Test main function parses commands correctly.

    :param mocker: pytest mocker fixture
    :param args: command line arguments
    :param expected_command: expected command enum value
    """
    mocker.patch('sys.argv', ['ruff_config_generator', *args])
    mock_download = mocker.patch('ruff_config_generator.main.download')
    mock_generate = mocker.patch('ruff_config_generator.main.generate_configuration')

    result = main()

    assert result == 0

    if expected_command in (Command.DOWNLOAD, Command.BOTH):
        mock_download.assert_called_once()
    else:
        mock_download.assert_not_called()

    if expected_command in (Command.GENERATE, Command.BOTH):
        mock_generate.assert_called_once()
    else:
        mock_generate.assert_not_called()


def test_main_download_only(mocker: MockerFixture) -> None:
    """
    Test main function with download command.

    :param mocker: pytest mocker fixture
    """
    mocker.patch('sys.argv', ['ruff_config_generator', 'download'])
    mock_download = mocker.patch('ruff_config_generator.main.download')
    mock_generate = mocker.patch('ruff_config_generator.main.generate_configuration')

    result = main()

    assert result == 0
    mock_download.assert_called_once()
    mock_generate.assert_not_called()


def test_main_generate_only(mocker: MockerFixture) -> None:
    """
    Test main function with generate command.

    :param mocker: pytest mocker fixture
    """
    mocker.patch('sys.argv', ['ruff_config_generator', 'generate'])
    mock_download = mocker.patch('ruff_config_generator.main.download')
    mock_generate = mocker.patch('ruff_config_generator.main.generate_configuration')

    result = main()

    assert result == 0
    mock_download.assert_not_called()
    mock_generate.assert_called_once()


def test_main_both_commands(mocker: MockerFixture) -> None:
    """
    Test main function with both command (default).

    :param mocker: pytest mocker fixture
    """
    mocker.patch('sys.argv', ['ruff_config_generator'])
    mock_download = mocker.patch('ruff_config_generator.main.download')
    mock_generate = mocker.patch('ruff_config_generator.main.generate_configuration')

    result = main()

    assert result == 0
    mock_download.assert_called_once()
    mock_generate.assert_called_once()


def test_main_download_exception(
    mocker: MockerFixture,
) -> None:
    """
    Test main function handles download exception.

    :param mocker: pytest mocker fixture
    """
    mocker.patch('sys.argv', ['ruff_config_generator', 'download'])
    mocker.patch('ruff_config_generator.main.download', side_effect=RuntimeError('Download failed'))

    with Logot(capturer=LoguruCapturer).capturing() as logot:
        result = main()
        logot.assert_logged(logged.error('Operation failed'))
    assert result == 1


def test_main_generate_exception(
    mocker: MockerFixture,
) -> None:
    """
    Test main function handles generate exception.

    :param mocker: pytest mocker fixture
    """
    mocker.patch('sys.argv', ['ruff_config_generator', 'generate'])
    mocker.patch(
        'ruff_config_generator.main.generate_configuration',
        side_effect=ValueError('Generation failed'),
    )

    with Logot(capturer=LoguruCapturer).capturing() as logot:
        result = main()
        logot.assert_logged(logged.error('Operation failed'))
    assert result == 1


def test_main_success_logging(
    mocker: MockerFixture,
) -> None:
    """
    Test main function logs success message.

    :param mocker: pytest mocker fixture
    """
    mocker.patch('sys.argv', ['ruff_config_generator', 'download'])
    mocker.patch('ruff_config_generator.main.download')

    with Logot(capturer=LoguruCapturer).capturing() as logot:
        result = main()
        logot.assert_logged(logged.info('Operation completed successfully'))
    assert result == 0
