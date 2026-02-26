import logging
from pathlib import Path

import bs4
import pytest
from pytest_mock import MockerFixture

from ruff_config_generator.generator import (
    _HtmlParser,
    generate_configuration,
    RuffConfiguration,
    Section,
    Setting,
)


class TestSetting:
    """Tests for the Setting class."""

    def test_init(self) -> None:
        """Test Setting initialization."""
        setting = Setting()

        assert setting.name is None
        assert setting.default_value is None
        assert setting.comments == []

    @pytest.mark.parametrize(
        ['default_value', 'expected'],
        [
            ('{}', False),
            (None, False),
            ('[]', False),
            ('true', False),
            ('{key: value}', True),
            ('{"key": "value"}', True),
        ],
    )
    def test_is_non_empty_dict(self, default_value: str | None, expected: bool) -> None:
        """
        Test is_non_empty_dict property.

        :param default_value: default value to test
        :param expected: expected result
        """
        setting = Setting()
        setting.default_value = default_value

        assert setting.is_non_empty_dict == expected

    def test_str_with_none_value(self) -> None:
        """Test string representation with None value."""
        setting = Setting()
        setting.name = 'test-setting'
        setting.default_value = None
        setting.comments = ['This is a comment']

        result = str(setting)

        assert '# This is a comment' in result
        assert '#test-setting =' in result

    def test_str_with_null_value(self) -> None:
        """Test string representation with null value."""
        setting = Setting()
        setting.name = 'test-setting'
        setting.default_value = 'null'
        setting.comments = []

        result = str(setting)

        assert '#test-setting =' in result

    def test_str_with_boolean_value(self) -> None:
        """Test string representation with boolean value."""
        setting = Setting()
        setting.name = 'test-setting'
        setting.default_value = 'true'

        result = str(setting)

        assert 'test-setting = true' in result

    def test_str_with_integer_value(self) -> None:
        """Test string representation with integer value."""
        setting = Setting()
        setting.name = 'line-length'
        setting.default_value = '88'

        result = str(setting)

        assert 'line-length = 88' in result

    def test_str_with_string_value(self) -> None:
        """Test string representation with string value."""
        setting = Setting()
        setting.name = 'output-format'
        setting.default_value = 'text'

        result = str(setting)

        assert 'output-format = "text"' in result

    def test_str_with_quoted_string(self) -> None:
        """Test string representation with already quoted string."""
        setting = Setting()
        setting.name = 'test-setting'
        setting.default_value = '"already-quoted"'

        result = str(setting)

        assert 'test-setting = "already-quoted"' in result

    def test_str_with_empty_list(self) -> None:
        """Test string representation with empty list."""
        setting = Setting()
        setting.name = 'select'
        setting.default_value = '[]'

        result = str(setting)

        assert 'select = []' in result

    def test_str_with_list_value(self) -> None:
        """Test string representation with list value."""
        setting = Setting()
        setting.name = 'select'
        setting.default_value = '["E", "F", "W"]'

        result = str(setting)

        assert 'select = [' in result
        assert '"E",' in result
        assert '"F",' in result
        assert '"W",' in result

    def test_str_with_dict_value(self) -> None:
        """Test string representation with dict value."""
        setting = Setting()
        setting.name = 'per-file-ignores'
        setting.default_value = '{"test.py": ["E501"]}'

        result = str(setting)

        assert 'per-file-ignores = {"test.py" = ["E501"]}' in result

    def test_str_with_regex_setting(self) -> None:
        """Test string representation with regex setting."""
        setting = Setting()
        setting.name = 'class-rgx'
        setting.default_value = '"^[A-Z][a-zA-Z0-9]*$"'

        result = str(setting)

        assert 'class-rgx = "^[A-Z][a-zA-Z0-9]*$"' in result

    def test_str_with_regex_setting_escaping(self) -> None:
        """Test string representation with regex setting requiring escaping."""
        setting = Setting()
        setting.name = 'function-rgx'
        setting.default_value = '"\\d+"'

        result = str(setting)

        assert 'function-rgx = "\\\\d+"' in result

    def test_get_comment_lines(self) -> None:
        """Test get_comment_lines method."""
        setting = Setting()
        setting.comments = ['First comment', 'Second comment']

        lines = setting.get_comment_lines()

        assert lines == ['# First comment', '# Second comment']

    def test_get_comment_lines_empty(self) -> None:
        """Test get_comment_lines with no comments."""
        setting = Setting()
        setting.comments = []

        lines = setting.get_comment_lines()

        assert lines == []


class TestSection:
    """Tests for the Section class."""

    def test_init(self) -> None:
        """Test Section initialization."""
        section = Section('lint')

        assert section.name == 'lint'
        assert section.settings == []

    def test_str_top_level_section(self) -> None:
        """Test string representation of top-level section."""
        section = Section('Top-level')
        setting = Setting()
        setting.name = 'line-length'
        setting.default_value = '88'
        setting.comments = []
        section.settings.append(setting)

        result = str(section)

        assert '[Top-level]' not in result
        assert 'line-length = 88' in result

    def test_str_regular_section(self) -> None:
        """Test string representation of regular section."""
        section = Section('lint')
        setting = Setting()
        setting.name = 'select'
        setting.default_value = '[]'
        setting.comments = []
        section.settings.append(setting)

        result = str(section)

        assert '[lint]' in result
        assert 'select = []' in result

    def test_str_with_dict_value_setting(self) -> None:
        """Test string representation with dict value setting."""
        section = Section('lint')
        setting = Setting()
        setting.name = 'per-file-ignores'
        setting.default_value = '{"test.py": ["E501"], "app.py": ["F401"]}'
        setting.comments = ['File-specific ignores']
        section.settings.append(setting)

        result = str(section)

        assert '[lint]' in result
        assert '# File-specific ignores' in result
        assert '[lint.per-file-ignores]' in result
        assert '"test.py" = ["E501"]' in result
        assert '"app.py" = ["F401"]' in result


class TestRuffConfiguration:
    """Tests for the RuffConfiguration class."""

    def test_init(self) -> None:
        """Test RuffConfiguration initialization."""
        config = RuffConfiguration('0.1.0')

        assert config.version == '0.1.0'
        assert config.sections == []

    def test_new_section(self) -> None:
        """Test new_section method."""
        config = RuffConfiguration('0.1.0')

        config.new_section('lint')
        config.new_section('format')

        assert len(config.sections) == 2
        assert config.sections[0].name == 'lint'
        assert config.sections[1].name == 'format'

    def test_add_setting(self) -> None:
        """Test add_setting method."""
        config = RuffConfiguration('0.1.0')
        config.new_section('lint')

        setting = Setting()
        setting.name = 'select'
        setting.default_value = '[]'
        config.add_setting(setting)

        assert len(config.sections[0].settings) == 1
        assert config.sections[0].settings[0].name == 'select'

    def test_str_basic(self) -> None:
        """Test string representation."""
        config = RuffConfiguration('0.1.0')
        config.new_section('Top-level')
        setting = Setting()
        setting.name = 'line-length'
        setting.default_value = '88'
        setting.comments = []
        config.add_setting(setting)

        result = str(config)

        assert '### Configuration created for ruff==0.1.0' in result
        assert 'line-length = 88' in result

    def test_str_with_rule_descriptions(self, mocker: MockerFixture) -> None:
        """
        Test string representation with rule descriptions.

        :param mocker: pytest mocker fixture
        """
        mocker.patch(
            'ruff_config_generator.generator.RULES_DESCRIPTIONS',
            {'E501': 'Line too long'},
        )

        config = RuffConfiguration('0.1.0')
        config.new_section('lint')
        setting = Setting()
        setting.name = 'ignore'
        setting.default_value = '["E501"]'
        setting.comments = []
        config.add_setting(setting)

        result = str(config)

        assert '"E501",' in result
        assert '# Line too long' in result

    def test_update_default_values(self) -> None:
        """Test update_default_values method."""
        config = RuffConfiguration('0.1.0')
        config.new_section('lint')

        setting1 = Setting()
        setting1.name = 'select'
        setting1.default_value = '[]'
        config.add_setting(setting1)

        setting2 = Setting()
        setting2.name = 'ignore'
        setting2.default_value = '[]'
        config.add_setting(setting2)

        update = {'lint': {'select': '["ALL"]', 'ignore': '["E501"]'}}

        config.update_default_values(update)

        assert config.sections[0].settings[0].default_value == '["ALL"]'
        assert config.sections[0].settings[1].default_value == '["E501"]'

    def test_update_default_values_removes_used_updates(self) -> None:
        """Test that update_default_values removes used updates."""
        config = RuffConfiguration('0.1.0')
        config.new_section('lint')
        setting = Setting()
        setting.name = 'select'
        setting.default_value = '[]'
        config.add_setting(setting)

        update = {'lint': {'select': '["ALL"]'}}
        original_update = update.copy()

        config.update_default_values(update)

        # Original dict should be unchanged (deepcopy is used)
        assert original_update == {'lint': {'select': '["ALL"]'}}

    def test_update_default_values_warns_on_not_found(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """
        Test update_default_values warns on not found overrides.

        :param caplog: pytest log capture fixture
        """
        config = RuffConfiguration('0.1.0')
        config.new_section('lint')

        update = {'format': {'quote-style': 'single'}}

        with caplog.at_level(logging.WARNING):
            config.update_default_values(update)

        assert 'Not found overrides' in caplog.text
        assert 'format' in caplog.text

    def test_update_default_values_skips_non_matching_settings(self) -> None:
        """Test update_default_values skips settings not in update dict."""
        config = RuffConfiguration('0.1.0')
        config.new_section('lint')

        setting1 = Setting()
        setting1.name = 'select'
        setting1.default_value = '[]'
        config.add_setting(setting1)

        setting2 = Setting()
        setting2.name = 'ignore'
        setting2.default_value = '[]'
        config.add_setting(setting2)

        # Only update 'select', not 'ignore'
        update = {'lint': {'select': '["ALL"]'}}

        config.update_default_values(update)

        assert config.sections[0].settings[0].default_value == '["ALL"]'
        assert config.sections[0].settings[1].default_value == '[]'  # Unchanged


class TestHtmlParser:
    """Tests for the _HtmlParser class."""

    def test_init(self) -> None:
        """Test _HtmlParser initialization."""
        config = RuffConfiguration('0.1.0')
        parser = _HtmlParser(config)

        assert parser.config is config
        assert parser.current_setting is None

    def test_handle_section_header_h2(self) -> None:
        """Test handling h2 section headers."""
        config = RuffConfiguration('0.1.0')
        parser = _HtmlParser(config)

        tag = bs4.BeautifulSoup('<h2>Lint Options</h2>', 'html.parser').h2
        assert tag is not None
        parser.parse_tag(tag)

        assert len(config.sections) == 1
        assert config.sections[0].name == 'Lint Options'

    def test_handle_section_header_h3(self) -> None:
        """Test handling h3 section headers."""
        config = RuffConfiguration('0.1.0')
        parser = _HtmlParser(config)

        tag = bs4.BeautifulSoup('<h3>Format Options</h3>', 'html.parser').h3
        assert tag is not None
        parser.parse_tag(tag)

        assert len(config.sections) == 1
        assert config.sections[0].name == 'Format Options'

    def test_handle_setting_header(self) -> None:
        """Test handling h4 setting headers."""
        config = RuffConfiguration('0.1.0')
        parser = _HtmlParser(config)

        tag = bs4.BeautifulSoup('<h4><code>line-length</code></h4>', 'html.parser').h4
        assert tag is not None
        parser.parse_tag(tag)

        assert parser.current_setting is not None
        assert parser.current_setting.name == 'line-length'

    def test_handle_paragraph_description(self) -> None:
        """Test handling paragraph as description."""
        config = RuffConfiguration('0.1.0')
        parser = _HtmlParser(config)
        parser.current_setting = Setting()

        tag = bs4.BeautifulSoup('<p>This is a description</p>', 'html.parser').p
        assert tag is not None
        parser.parse_tag(tag)

        assert parser.current_setting.comments == ['This is a description']

    def test_handle_paragraph_default_value(self) -> None:
        """Test handling paragraph with default value."""
        config = RuffConfiguration('0.1.0')
        config.new_section('lint')
        parser = _HtmlParser(config)
        parser.current_setting = Setting()
        parser.current_setting.name = 'select'

        tag = bs4.BeautifulSoup(
            '<p>Default value: <code>[]</code></p>',
            'html.parser',
        ).p
        assert tag is not None
        parser.parse_tag(tag)

        assert len(config.sections[0].settings) == 1
        assert config.sections[0].settings[0].default_value == '[]'
        assert parser.current_setting is None

    def test_handle_paragraph_ignores_when_no_current_setting(self) -> None:
        """Test that paragraph is ignored when no current setting."""
        config = RuffConfiguration('0.1.0')
        parser = _HtmlParser(config)

        tag = bs4.BeautifulSoup('<p>Random paragraph</p>', 'html.parser').p
        assert tag is not None
        parser.parse_tag(tag)

        # Should not raise an error
        assert parser.current_setting is None

    def test_handle_list(self) -> None:
        """Test handling unordered lists."""
        config = RuffConfiguration('0.1.0')
        parser = _HtmlParser(config)
        parser.current_setting = Setting()

        tag = bs4.BeautifulSoup(
            '<ul><li>First item</li><li>Second item</li></ul>',
            'html.parser',
        ).ul
        assert tag is not None
        parser.parse_tag(tag)

        assert '- First item' in parser.current_setting.comments
        assert '- Second item' in parser.current_setting.comments

    def test_handle_list_ignores_when_no_current_setting(self) -> None:
        """Test that list is ignored when no current setting."""
        config = RuffConfiguration('0.1.0')
        parser = _HtmlParser(config)

        tag = bs4.BeautifulSoup('<ul><li>Item</li></ul>', 'html.parser').ul
        assert tag is not None
        parser.parse_tag(tag)

        # Should not raise an error
        assert parser.current_setting is None

    def test_handle_list_with_non_tag_children(self) -> None:
        """Test handling list with text nodes and non-li tags."""
        config = RuffConfiguration('0.1.0')
        parser = _HtmlParser(config)
        parser.current_setting = Setting()

        # Create a list with text nodes and non-li elements
        html = '<ul>Text node<li>Item 1</li><div>Not an li</div><li>Item 2</li></ul>'
        tag = bs4.BeautifulSoup(html, 'html.parser').ul
        assert tag is not None
        parser.parse_tag(tag)

        # Should only process li elements
        assert '- Item 1' in parser.current_setting.comments
        assert '- Item 2' in parser.current_setting.comments
        assert 'Text node' not in parser.current_setting.comments
        assert 'Not an li' not in parser.current_setting.comments

    def test_handle_div_deprecated(self) -> None:
        """Test handling deprecated setting in div."""
        config = RuffConfiguration('0.1.0')
        parser = _HtmlParser(config)
        parser.current_setting = Setting()
        parser.current_setting.name = 'old-setting'

        tag = bs4.BeautifulSoup('<div>Deprecated: use new-setting instead</div>', 'html.parser').div
        assert tag is not None
        parser.parse_tag(tag)

        assert parser.current_setting is None

    def test_handle_div_code_example(self) -> None:
        """Test handling code example in div."""
        config = RuffConfiguration('0.1.0')
        parser = _HtmlParser(config)
        parser.current_setting = Setting()

        tag = bs4.BeautifulSoup(
            '<div class="highlight">line-length = 88</div>',
            'html.parser',
        ).div
        assert tag is not None
        parser.parse_tag(tag)

        assert '---' in parser.current_setting.comments
        assert 'line-length = 88' in parser.current_setting.comments

    def test_handle_div_ignores_when_no_current_setting(self) -> None:
        """Test that div is ignored when no current setting."""
        config = RuffConfiguration('0.1.0')
        parser = _HtmlParser(config)

        tag = bs4.BeautifulSoup('<div>Random div</div>', 'html.parser').div
        assert tag is not None
        parser.parse_tag(tag)

        # Should not raise an error
        assert parser.current_setting is None


def test_generate_configuration_success(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    """
    Test successful configuration generation.

    :param mocker: pytest mocker fixture
    :param tmp_path: pytest temporary directory fixture
    """
    settings_file = tmp_path / 'settings.html'
    version_file = tmp_path / 'version.txt'
    config_file = tmp_path / 'config.toml'
    adjusted_config_file = tmp_path / 'config_adjusted.toml'

    html_content = """
    <article>
        <h2>Top-level</h2>
        <h4><code>line-length</code></h4>
        <p>The line length.</p>
        <p>Default value: <code>88</code></p>
    </article>
    """
    settings_file.write_text(html_content, encoding='utf-8')
    version_file.write_text('0.1.0', encoding='utf-8')

    mocker.patch('ruff_config_generator.generator.SETTINGS_HTML_FILE', settings_file)
    mocker.patch('ruff_config_generator.generator.VERSION_FILE', version_file)
    mocker.patch('ruff_config_generator.generator.CONFIGURATION_FILE', config_file)
    mocker.patch('ruff_config_generator.generator.ADJUSTED_CONFIGURATION_FILE', adjusted_config_file)
    mocker.patch('ruff_config_generator.generator.OVERRIDE_DEFAULT_VALUES', {})

    generate_configuration()

    assert config_file.exists()
    assert adjusted_config_file.exists()

    content = config_file.read_text(encoding='utf-8')
    assert 'ruff==0.1.0' in content
    assert 'line-length = 88' in content


def test_generate_configuration_missing_article(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    """
    Test configuration generation with missing article element.

    :param mocker: pytest mocker fixture
    :param tmp_path: pytest temporary directory fixture
    """
    settings_file = tmp_path / 'settings.html'
    version_file = tmp_path / 'version.txt'

    html_content = '<html><body><p>No article here</p></body></html>'
    settings_file.write_text(html_content, encoding='utf-8')
    version_file.write_text('0.1.0', encoding='utf-8')

    mocker.patch('ruff_config_generator.generator.SETTINGS_HTML_FILE', settings_file)
    mocker.patch('ruff_config_generator.generator.VERSION_FILE', version_file)

    with pytest.raises(ValueError, match='Could not find <article> element'):
        generate_configuration()


def test_generate_configuration_with_overrides(
    mocker: MockerFixture,
    tmp_path: Path,
) -> None:
    """
    Test configuration generation with override values.

    :param mocker: pytest mocker fixture
    :param tmp_path: pytest temporary directory fixture
    """
    settings_file = tmp_path / 'settings.html'
    version_file = tmp_path / 'version.txt'
    config_file = tmp_path / 'config.toml'
    adjusted_config_file = tmp_path / 'config_adjusted.toml'

    html_content = """
    <article>
        <h2>Top-level</h2>
        <h4><code>line-length</code></h4>
        <p>The line length.</p>
        <p>Default value: <code>88</code></p>
    </article>
    """
    settings_file.write_text(html_content, encoding='utf-8')
    version_file.write_text('0.1.0', encoding='utf-8')

    mocker.patch('ruff_config_generator.generator.SETTINGS_HTML_FILE', settings_file)
    mocker.patch('ruff_config_generator.generator.VERSION_FILE', version_file)
    mocker.patch('ruff_config_generator.generator.CONFIGURATION_FILE', config_file)
    mocker.patch('ruff_config_generator.generator.ADJUSTED_CONFIGURATION_FILE', adjusted_config_file)
    mocker.patch(
        'ruff_config_generator.generator.OVERRIDE_DEFAULT_VALUES',
        {'Top-level': {'line-length': '110'}},
    )

    generate_configuration()

    default_content = config_file.read_text(encoding='utf-8')
    adjusted_content = adjusted_config_file.read_text(encoding='utf-8')

    assert 'line-length = 88' in default_content
    assert 'line-length = 110' in adjusted_content
