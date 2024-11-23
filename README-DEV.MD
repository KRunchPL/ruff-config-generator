# Developer information

This file contains the most important developer information for the repository.

## Cloning the repository

Of course this repository is cloned as all others, with `git clone` command, but there is one additional issuee you should be aware of before proceeding.

## Symlinks

All developers tools' configuration files are kept in a directory `.config`. Most of the tools are by default looking for configuration files under specific names in the CWD. In order to use configuration files from different paths, one must specify the path in the command line. In order to avoid this inconvenience, the main folder of repository contains symlinks to proper files of `.config` directory.

### Checking for symlink permissions

Before cloning a repository, make sure that you can create symlinks in the folder that you will be cloning into. If git will establish a lack of permissions, it will clone the repository, but the symlinks will be broken (they will be simple text files containing a path to the original file). That is why it is important to check for permissions and fix them if necessary.

#### Linux / MacOS

Make sure you have symlinks enabled globally in git:

```bash
git config --global core.symlinks true
```

Execute the following commands:

```bash
ln -s existing_source_file symbolic_link
ls -l | grep symbolic_link
rm symbolic_link
```

The output should not contain any errors and should look something like this:

```raw
lrwxrwxrwx 1 user user   20 Nov  9 21:36 symbolic_link -> existing_source_file
```

#### Windows

Make sure you have symlinks enabled globally in git:

```bash
git config --global core.symlinks true
```

Execute the following commands in `cmd` (NOT in Powershell):

```cmd
mklink symbolic_link existing_source_file & dir | findstr /c:"symbolic_link" & del symbolic_link
```

The output should not contain any errors and should look something like this:

```raw
symbolic link created for symbolic_link <<===>> existing_source_file
09.11.2023  23:20    <SYMLINK>      symbolic_link [existing_source_file]
```

Especially you should NOT see:

```raw
You do not have sufficient privilege to perform this operation.
```

### Fixing symlink permissions

If you don't have permission to create symlinks, this section describes how to fix it.

#### Windows

1. Click `Win + R`, type `gpedit.msc` and click `Enter`.
1. In the left / "folder" part of window go to: `Computer Configuration -> Windows Settings -> Security Settings -> Local Policies -> User Rights Assignment`.
1. In the right part of the window find `Create symbolic links` and double click (or right-click and select `Properties`).
1. In the new window click `Add User or Group...` button.
1. In the only editable field (`Enter the object names to select`) enter your Windows username.
1. Click the `Check Names` button and wait until the username you entered gets resolved to something like `COMPUTER-NAME\username`.
1. Click the `OK` button in the window.
1. Click the `OK` button in the window.
1. Restart Windows.
1. Verify that you have permissions to create symlinks.
1. See [Git settings](#git-settings) below.

Reference: [Allowing non-administrators to create symbolic links](https://github.com/git-for-windows/git/wiki/Symbolic-Links#allowing-non-administrators-to-create-symbolic-links)

#### Git settings

If you have already cloned a repository that uses symlinks before fixing system's permission, you will probably need to change settings in it. Even if you have option `core.symlinks` enabled in your global git configuration, when during repository cloning git finds out that you don't have permissions to create symlink, it will set `core.symlinks` to false in the repository settings.

To make sure local repository configuration is not overriding the global setting, execute the following command IN THE REPOSITORY FOLDER:

```bash
git config --unset core.symlinks
```

## Python

Python part of the code shall follow those base guidelines:

* is compatible with Python version >=3.12.0,
* all code shall pass configured static code checks,
* all defined unit test shall pass,
* all code shall be covered by unit tests.

### Library dependencies

Project is using [Poetry](https://python-poetry.org/) to manage dependencies and building packages.

To install Poetry on your system follow the guide here: [Poetry Installation](https://python-poetry.org/docs/#installation)

If you want to have virtualenv created in `.venv` folder in repository root, configure Poetry with following command:

```console
poetry config virtualenvs.in-project true
```

To create a venv and install all dependencies:

```console
poetry install --no-root --sync
```

To add a production dependency:

```console
poetry add <dependency name>
```

To add a development dependency (like one used by tests):

```console
poetry add --group dev <dependency name>
```

To build new package:

```console
poetry build
```

### Unit tests

Unit tests shall be written using pytest and put in the `tests` directory in the repository root. For dependencies handling see [Dependencies section](#library-dependencies).

To run all the unit tests use the `pytest` command without any parameters in the main folder of the repo. This will start all the unit tests from the `tests` package and count coverage for every python file in the project package.

Results will be written to standard output. Coverage can be found in the `.coverage` file and the HTML version of the report will be put in the `coverage-report` directory.

Pytest configuration is in the `pytest.ini` file. Coverage report configuration is in the `.coveragerc` file.

### Static code checkers

Static checkers are being run on the repository by the PR checker, and therefore they shall be executed before submitting PR either locally or automatically when pushing branch to repository.

#### Linter

`ruff` is the linter of choice for this repository. Additionally, `darglint` is used to check docstrings content (arguments, returns, etc.). As `darglint` has limited configuration capabilities when it comes to choosing linted files, `flake8` is used as `darglint`'s wrapper.

To lint all python code use the `ruff .` and `flake8` commands in the main folder of the repo.

Full linting reports from both tools will be written to standard output.

`flake8` and `darglint` configuration is in the `.flake8` file.

`ruff` configuration is in the `ruff.toml` file.

#### Typing checks

`mypy` is the checker of choice for type checking on this repo.

To check all python code use the `mypy` command without any parameters in the main folder of the repo.

`mypy` configuration is in the `mypy.ini` file.

#### Auto formatter

`ruff` is the formatter of choice on this repo.

To format the whole repo code use `ruff format .`. The PR checker is making sure that the whole code is formatted using this command.

`ruff` configuration is in the `ruff.toml` file.
