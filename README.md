# Ruff Default Configuration Generator

Tool that generates [`ruff`](https://github.com/astral-sh/ruff) configuration with all available options set to their defualt values.

## Usage

```console
python -m ruff_config_generator download
python -m ruff_config_generator generate
```

The first command will download the settings HTML page and the second will analyze it and generate `toml` file with all available options set to their defualt values. The file will also contain options descriptions as comments.

Output files will be saved in the `workdir` folder as `settings.html` and `config.toml`.

On the repository, the `workdir` folder contains result of the above commands for latest ruff version I have been using. It also contains `config_adjusted.toml` which contains latest configuration with values adjusted to my personal projects.

## Additional documentation

[Development documentation](README-DEV.md)

[Changelog](CHANGELOG.md)
