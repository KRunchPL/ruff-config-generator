from functools import cached_property
from pathlib import Path
from typing import Any

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


_DEFAULT_CONFIG = (Path(__file__).parent / 'default_config.toml').absolute()


class AppConfiguration(BaseSettings):
    """
    Application configuration model.
    """

    workdir: Path
    settings_html_file_name: str
    version_file_name: str
    default_values_file_name: str
    adjusted_values_file_name: str
    overrides: dict[str, dict[str, Any]]
    rules_descriptions: dict[str, str]

    @cached_property
    def settings_html_file(self) -> Path:
        """
        File where HTML version of ruff settings is downloaded.

        :return: settings.html file path
        """
        return self.workdir / self.settings_html_file_name

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

    model_config = SettingsConfigDict(toml_file=_DEFAULT_CONFIG)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Model configuration.

        :param settings_cls: settings class
        :param init_settings: source for init settings
        :param env_settings: source for env settings
        :param dotenv_settings: source for dotenv settings
        :param file_secret_settings: source for file secret settings
        :return: tuple of sources
        """
        _ = init_settings, env_settings, dotenv_settings, file_secret_settings
        custom_path = init_settings.init_kwargs.get('toml_file')  # type: ignore [attr-defined]
        if custom_path:
            return (
                TomlConfigSettingsSource(
                    settings_cls,
                    toml_file=[_DEFAULT_CONFIG, custom_path],
                    deep_merge=True,
                ),
            )
        return (TomlConfigSettingsSource(settings_cls),)


_app_config = AppConfiguration()  # type: ignore [call-arg]


def set_app_config(new_app_config: AppConfiguration) -> None:
    """
    Override global app_config.

    :param new_app_config: new instance
    """
    global _app_config  # noqa: PLW0603
    _app_config = new_app_config


def get_app_config() -> AppConfiguration:
    """
    Return global app_config.

    :return: global app_config
    """
    return _app_config
