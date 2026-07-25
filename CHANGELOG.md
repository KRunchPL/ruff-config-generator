# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-07-25

### Added

- `workdir` is created if it does not exist
- Additional script name `ruff-config-generator` (the same as project name) is available
- Tool is published on pypi

## [2.0.0] - 2026-07-25

### Changed

- Support for deep merging app configuration provided with `--config` argument with the default one
- Dynamic rules downloading instead of hardcoding them in app configuration
- Rewriting for typer

### Removed

- Ability to run just one of the commands
- KRunchPL overrides are no longer included in the default app configuration

## [1.1.0] - 2025-02-26

### Added

- Allow specifying configuration as a TOML file

## [1.0.0] - 2025-02-08

### Added

- When running the script without parameters it will download the latests documentation and generate two configuration files.

## [0.1.0] - 2024-11-23

### Added

- Downloading `ruff` settings page and generating `toml` file with all available options set to their defualt values. The file also contains options' descriptions as fields comments.
