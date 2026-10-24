# Ruff Configuration Generator

Tool that generates [`ruff`](https://github.com/astral-sh/ruff) configuration with all available options.

## Usage

```console
ruff-config-generator [--config adjustments.toml]
```

The command will download the settings HTML page, analyze it, and generate two `toml` files. Both `toml` files will contain all available `ruff` options along with their descriptions. The difference between the two files is that one will have all settings set to their default values, while the other will have values adjusted according to provided config file.

For an example of `adjustments.toml` file, see `krunch_pl_config.toml` on the repository.

Output files will be saved in the `workdir` folder as `settings.html`, `default.toml` (default values) and `adjusted.toml`.

On the repository, the `workdir` folder contains result of the above command for latest ruff version I have been using.

## Additional documentation

[Development documentation](README-DEV.md)

[Changelog](CHANGELOG.md)
