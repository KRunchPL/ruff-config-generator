import bs4

from .configuration import SETTINGS_HTML_FILE, TOML_CONFIGURATION_FILE


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
        self.configs: list[Setting] = []

    def __str__(self) -> str:
        lines: list[str] = []
        dict_value_configs = []
        if self.name != 'Top-level':
            lines.append(f'[{self.name}]')
        for config in self.configs:
            if config.is_non_empty_dict:
                dict_value_configs.append(config)
                continue
            lines.append(str(config))
        for config in dict_value_configs:
            assert config.default_value is not None
            lines.append('')
            lines.extend(config.get_comment_lines())
            lines.append(f'[{self.name}.{config.name}]')
            values = '\n'.join(config.default_value[1:-1].replace('":', '" =').split(', '))

            lines.append(values)
        lines.append('')
        return '\n'.join(lines)


def generate_toml_configuration() -> None:  # noqa: C901, PLR0912
    """
    Generate TOML file configuration.
    """
    page = bs4.BeautifulSoup(SETTINGS_HTML_FILE.read_text(encoding='utf-8'), 'html.parser')
    article = page.find(name='article')
    sections = []

    current_config = None

    for tag in article.children:  # type: ignore [union-attr]
        if tag.name == 'h2':  # type: ignore [union-attr]
            sections.append(Section(tag.text[:-1]))
        elif tag.name == 'h3':  # type: ignore [union-attr]
            assert current_config is None
            current_config = Setting()
            current_config.name = tag.find_next('code').get_text()  # type: ignore [union-attr]
        elif tag.name == 'p':  # type: ignore [union-attr]
            if current_config is None:
                continue
            if tag.get_text().startswith('Default value:'):
                current_config.default_value = tag.find_next('code').get_text()  # type: ignore [union-attr]
                sections[-1].configs.append(current_config)
                current_config = None
                continue
            current_config.comments.extend(tag.get_text().splitlines())
        elif tag.name == 'ul':  # type: ignore [union-attr]
            if current_config is None:
                continue
            for ul_child in tag.children:  # type: ignore [union-attr]
                if ul_child.name != 'li':
                    continue
                current_config.comments.extend(f'- {ul_child.get_text()}'.splitlines())
        elif tag.name == 'div':  # type: ignore [union-attr]
            if current_config is None:
                continue
            if tag.get_text().strip().startswith('Deprecated'):
                current_config = None
                continue
            if tag['class'] != ['highlight']:  # type: ignore [index]
                continue
            current_config.comments.extend(['---', *tag.get_text().splitlines(), '---'])

    with TOML_CONFIGURATION_FILE.open('w', encoding='utf-8') as file:
        for section in sections:
            file.write(str(section))
            file.write('\n')
