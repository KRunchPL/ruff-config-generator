from copy import deepcopy

import bs4

from .configuration import (
    ADJUSTED_CONFIGURATION_FILE,
    CONFIGURATION_FILE,
    OVERRIDE_DEFAULT_VALUES,
    RULES_DESCRIPTIONS,
    SETTINGS_HTML_FILE,
    VERSION_FILE,
)


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
        if self.name.endswith('-rgx'):
            value = self.default_value.strip('"').replace('\\', '\\\\')
            return f'"{value}"'
        if self.default_value in {'true', 'false', '[]', r'{}'} or self.default_value.startswith('"'):
            return self.default_value
        try:
            int(self.default_value)
        except ValueError:
            pass
        else:
            return self.default_value
        if self.default_value.startswith('['):
            values = ',\n    '.join(self.default_value[1:-1].split(', '))
            return f'[\n    {values},\n]'
        if self.default_value.startswith('{'):
            return self.default_value.replace('":', '" =')

        return f'"{self.default_value}"'


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
            if description := RULES_DESCRIPTIONS.get(rule_id):
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
            print(f'Not found overrides: {update}')  # noqa: T201


def generate_configuration() -> None:  # noqa: C901, PLR0912
    """
    Generate TOML file configuration.
    """
    e_page = bs4.BeautifulSoup(SETTINGS_HTML_FILE.read_text(encoding='utf-8'), 'html.parser')
    e_article = e_page.find(name='article')
    config = RuffConfiguration(VERSION_FILE.read_text(encoding='utf-8'))
    current_setting = None

    for tag in e_article.children:  # type: ignore [union-attr]
        if tag.name in ('h2', 'h3'):  # type: ignore [union-attr]
            config.new_section(tag.text)
        elif tag.name == 'h4':  # type: ignore [union-attr]
            assert current_setting is None
            current_setting = Setting()
            current_setting.name = tag.find_next('code').get_text()  # type: ignore [union-attr]
        elif tag.name == 'p':  # type: ignore [union-attr]
            if current_setting is None:
                continue
            if tag.get_text().startswith('Default value:'):
                current_setting.default_value = tag.find_next('code').get_text()  # type: ignore [union-attr]
                config.add_setting(current_setting)
                current_setting = None
                continue
            current_setting.comments.extend(tag.get_text().splitlines())
        elif tag.name == 'ul':  # type: ignore [union-attr]
            if current_setting is None:
                continue
            for ul_child in tag.children:  # type: ignore [union-attr]
                if ul_child.name != 'li':
                    continue
                current_setting.comments.extend(f'- {ul_child.get_text()}'.splitlines())
        elif tag.name == 'div':  # type: ignore [union-attr]
            if current_setting is None:
                continue
            if tag.get_text().strip().startswith('Deprecated'):
                current_setting = None
                continue
            if tag['class'] != ['highlight']:  # type: ignore [index]
                continue
            current_setting.comments.extend(['---', *tag.get_text().splitlines(), '---'])

    CONFIGURATION_FILE.write_text(str(config), encoding='utf-8')
    config.update_default_values(OVERRIDE_DEFAULT_VALUES)
    ADJUSTED_CONFIGURATION_FILE.write_text(str(config), encoding='utf-8')
