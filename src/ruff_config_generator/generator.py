import logging
from copy import deepcopy

import bs4

from .app_config import get_app_config


logger = logging.getLogger(__name__)


class Setting:
    """
    Single ruff setting.
    """

    def __init__(self) -> None:
        self.name: str | None = None
        self.default_value: str | None = None
        self.comments: list[str] = []

    @property
    def is_non_empty_dict(self) -> bool:
        """
        Indicates whether setting's default value is a non-empty dictionary.

        :return: whether setting's default value is a non-empty dictionary
        """
        return (
            self.default_value is not None
            and self.default_value != r'{}'
            and self.default_value.startswith('{')
            and self.default_value.endswith('}')
        )

    def __str__(self) -> str:
        lines: list[str] = []
        lines.extend(self.get_comment_lines())
        if self.default_value in {'None', 'null', None}:
            lines.append(f'#{self.name} =')
        else:
            lines.append(f'{self.name} = {self._processed_default_value()}')
        return '\n'.join(lines)

    def get_comment_lines(self) -> list[str]:
        """
        Generate a list of comment lines.

        :return: list of comment lines
        """
        return [f'# {comment}'.strip() for comment in self.comments]

    def _processed_default_value(self) -> str:
        assert self.name is not None
        assert self.default_value is not None

        # Regex patterns need special escaping
        if self._is_regex_setting():
            return self._process_regex_value()

        # Pass through booleans, empty collections, and quoted strings
        if self._is_passthrough_value():
            return self.default_value

        # Integers don't need quotes
        if self._is_integer_value():
            return self.default_value

        # Format list values with proper indentation
        if self._is_list_value():
            return self._process_list_value()

        # Convert dict format from JSON to TOML
        if self._is_dict_value():
            return self.default_value.replace('":', '" =')

        # Default: wrap in quotes  # noqa: ERA001
        return f'"{self.default_value}"'

    def _is_regex_setting(self) -> bool:
        assert self.name is not None
        return self.name.endswith('-rgx')

    def _process_regex_value(self) -> str:
        assert self.default_value is not None
        value = self.default_value.strip('"').replace('\\', '\\\\')
        return f'"{value}"'

    def _is_passthrough_value(self) -> bool:
        assert self.default_value is not None
        return self.default_value in {'true', 'false', '[]', r'{}'} or self.default_value.startswith('"')

    def _is_integer_value(self) -> bool:
        assert self.default_value is not None
        try:
            int(self.default_value)
        except ValueError:
            return False
        else:
            return True

    def _is_list_value(self) -> bool:
        assert self.default_value is not None
        return self.default_value.startswith('[')

    def _process_list_value(self) -> str:
        assert self.default_value is not None
        values = ',\n    '.join(self.default_value[1:-1].split(', '))
        return f'[\n    {values},\n]'

    def _is_dict_value(self) -> bool:
        assert self.default_value is not None
        return self.default_value.startswith('{')


class Section:
    """
    Single ruff configuration section.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.settings: list[Setting] = []

    def __str__(self) -> str:
        lines: list[str] = []
        dict_value_settings = []
        if self.name != 'Top-level':
            lines.append(f'[{self.name}]')
        for setting in self.settings:
            if setting.is_non_empty_dict:
                dict_value_settings.append(setting)
                continue
            lines.append(str(setting))
        for setting in dict_value_settings:
            assert setting.default_value is not None
            lines.append('')
            lines.extend(setting.get_comment_lines())
            lines.append(f'[{self.name}.{setting.name}]')
            values = '\n'.join(setting.default_value[1:-1].replace('":', '" =').split(', '))

            lines.append(values)
        lines.append('')
        return '\n'.join(lines)


class RuffConfiguration:
    """
    Whole Ruff configuration.
    """

    def __init__(self, version: str) -> None:
        self.version = version
        self.sections: list[Section] = []

    def new_section(self, name: str) -> None:
        """
        Start new section.

        :param name: section name
        """
        self.sections.append(Section(name))

    def add_setting(self, setting: Setting) -> None:
        """
        Add setting to latest section.

        :param setting: setting to be added
        """
        self.sections[-1].settings.append(setting)

    def __str__(self) -> str:
        lines: list[str] = []
        lines.append(f'### Configuration created for ruff=={self.version}')
        lines.append('')
        lines.extend(str(section) for section in self.sections)
        lines = ('\n'.join(lines)).splitlines()
        for index, line in enumerate(lines):
            rule_id = line.strip(' ",')
            if description := get_app_config().rules_descriptions.get(rule_id):
                spaces = ' ' * (9 - len(rule_id))
                lines[index] = f'{line}{spaces}# {description}'
        lines.append('')
        return '\n'.join(lines)

    def update_default_values(self, update: dict[str, dict[str, str]]) -> None:
        """
        Update default values in settings according to provided dict.

        :param update: new default values for settings
        """
        update = deepcopy(update)
        for section in self.sections:
            if section.name not in update:
                continue
            section_update = update[section.name]
            for setting in section.settings:
                if setting.name not in section_update:
                    continue
                setting.default_value = section_update.pop(setting.name)
            if not section_update:
                update.pop(section.name)
        if update:
            logger.warning('Not found overrides: %s', update)


class _HtmlParser:
    """Parser for ruff settings HTML documentation."""

    def __init__(self, config: RuffConfiguration) -> None:
        self.config = config
        self.current_setting: Setting | None = None

    def parse_tag(self, tag: bs4.Tag) -> None:
        """
        Parse a single HTML tag and update configuration.

        :param tag: HTML tag to parse
        """
        if tag.name in ('h2', 'h3'):
            self._handle_section_header(tag)
        elif tag.name == 'h4':
            self._handle_setting_header(tag)
        elif tag.name == 'p':
            self._handle_paragraph(tag)
        elif tag.name == 'ul':
            self._handle_list(tag)
        elif tag.name == 'div':
            self._handle_div(tag)

    def _handle_section_header(self, tag: bs4.Tag) -> None:
        """
        Handle h2/h3 section headers.

        :param tag: section header tag to parse
        """
        self.config.new_section(tag.text)
        logger.debug('Created section: %s', tag.text)

    def _handle_setting_header(self, tag: bs4.Tag) -> None:
        """
        Handle h4 setting headers.

        :param tag: setting header tag to parse
        """
        assert self.current_setting is None, 'Found h4 while processing previous setting'
        self.current_setting = Setting()
        code_element = tag.find_next('code')
        assert code_element is not None, 'h4 tag must contain a code element'
        self.current_setting.name = code_element.get_text()
        logger.debug('Started setting: %s', self.current_setting.name)

    def _handle_paragraph(self, tag: bs4.Tag) -> None:
        """
        Handle paragraph tags (descriptions or default values).

        :param tag: paragraph tag to parse
        """
        if self.current_setting is None:
            return

        text = tag.get_text()
        if text.startswith('Default value:'):
            code_element = tag.find_next('code')
            assert code_element is not None, 'Default value paragraph must contain a code element'
            self.current_setting.default_value = code_element.get_text()
            self.config.add_setting(self.current_setting)
            logger.debug('Completed setting: %s', self.current_setting.name)
            self.current_setting = None
        else:
            self.current_setting.comments.extend(text.splitlines())

    def _handle_list(self, tag: bs4.Tag) -> None:
        """
        Handle unordered list tags (setting options/notes).

        :param tag: unordered list tag to parse
        """
        if self.current_setting is None:
            return

        for ul_child in tag.children:
            if not isinstance(ul_child, bs4.Tag) or ul_child.name != 'li':
                continue
            self.current_setting.comments.extend(f'- {ul_child.get_text()}'.splitlines())

    def _handle_div(self, tag: bs4.Tag) -> None:
        """
        Handle div tags (code examples or deprecation notices).

        :param tag: div tag to parse
        """
        if self.current_setting is None:
            return

        text = tag.get_text().strip()
        if text.startswith('Deprecated'):
            logger.debug('Skipping deprecated setting: %s', self.current_setting.name)
            self.current_setting = None
            return

        if tag.get('class') == ['highlight']:
            self.current_setting.comments.extend(['---', *tag.get_text().splitlines(), '---'])


def generate_configuration() -> None:
    """
    Generate TOML file configuration.

    :raises ValueError: if HTML structure is unexpected
    """
    logger.info('Starting configuration generation')

    # Load HTML and version
    html_content = get_app_config().settings_html_file.read_text(encoding='utf-8')
    version = get_app_config().version_file.read_text(encoding='utf-8').strip()
    logger.info('Generating configuration for ruff version %s', version)

    # Parse HTML
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    article = soup.find(name='article')
    if article is None:
        msg = 'Could not find <article> element in settings HTML'
        raise ValueError(msg)

    # Build configuration
    config = RuffConfiguration(version)
    parser = _HtmlParser(config)

    for tag in article.children:  # type: ignore [union-attr]
        if isinstance(tag, bs4.Tag):
            parser.parse_tag(tag)

    # Write output files
    logger.info('Writing configuration to %s', get_app_config().default_values_file)
    get_app_config().default_values_file.write_text(str(config), encoding='utf-8')

    config.update_default_values(get_app_config().overrides)
    logger.info('Writing adjusted configuration to %s', get_app_config().adjusted_values_file)
    get_app_config().adjusted_values_file.write_text(str(config), encoding='utf-8')

    logger.info('Configuration generation completed')
