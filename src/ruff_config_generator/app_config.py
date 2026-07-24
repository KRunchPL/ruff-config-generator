from functools import cached_property
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class AppConfiguration(BaseModel):
    """
    Application configuration model.
    """

    workdir: Path
    settings_html_file_name: str
    rules_html_file_name: str
    version_file_name: str
    default_values_file_name: str
    adjusted_values_file_name: str
    overrides: dict[str, dict[str, Any]]

    @cached_property
    def settings_html_file(self) -> Path:
        """
        File where HTML version of ruff settings is downloaded.

        :return: settings.html file path
        """
        return self.workdir / self.settings_html_file_name

    @cached_property
    def rules_html_file(self) -> Path:
        """
        File where HTML version of ruff rules is downloaded.

        :return: rules.html file path
        """
        return self.workdir / self.rules_html_file_name

    @cached_property
    def version_file(self) -> Path:
        """
        File where latest processed version of ruff is stored.

        :return: version.txt file path
        """
        return self.workdir / self.version_file_name

    @cached_property
    def default_values_file(self) -> Path:
        """
        File where ruff config with default values is generated.

        :return: ruff.toml with default values file path
        """
        return self.workdir / self.default_values_file_name

    @cached_property
    def adjusted_values_file(self) -> Path:
        """
        File where ruff config with adjusted values is generated.

        :return: ruff.toml with adjusted values file path
        """
        return self.workdir / self.adjusted_values_file_name
