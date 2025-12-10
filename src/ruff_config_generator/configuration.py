from pathlib import Path
from typing import Any


WORKDIR = Path('workdir')
SETTINGS_HTML_FILE = WORKDIR / 'settings.html'
VERSION_FILE = WORKDIR / 'version.txt'
CONFIGURATION_FILE = WORKDIR / 'config.toml'
ADJUSTED_CONFIGURATION_FILE = WORKDIR / 'config_adjusted.toml'
OVERRIDE_DEFAULT_VALUES: dict[str, dict[str, Any]] = {
    'Top-level': {
        'line-length': '110',
        'output-format': 'concise',
        'target-version': 'py314',
    },
    'analyze': {
        'direction': 'Dependencies',
    },
    'format': {
        'docstring-code-format': 'true',
        'line-ending': 'lf',
        'quote-style': 'single',
    },
    'lint': {
        'external': '["DAR"]',
        'ignore': """\
["B005",
    "D100",
    "D104",
    "D105",
    "D107",
    "D200",
    "D203",
    "D212",
    "RUF012",
    "S101",
    "TC001",
    "TC002",
    "TC003",
    "PYI041"]""",
        'select': '["ALL"]',
        'per-file-ignores': """\
{"!tests/*" = [
    "PT",
]
"tests/*" = [
    "SLF001",
    "FBT001",
    "PLR0913",
    "RUF018",
]
"tests/**/test_*" = [
    "ANN",
    "D101",
    "D102",
    "D103",
    "B011",
    "PLR2004",
]}""",
    },
    'lint.flake8-import-conventions': {
        'banned-from': '["yaml", "json", "tomllib"]',
    },
    'lint.flake8-pytest-style': {
        'parametrize-names-type': 'list',
    },
    'lint.flake8-quotes': {
        'inline-quotes': 'single',
    },
    'lint.isort': {
        'combine-as-imports': 'true',
        'lines-after-imports': '2',
        'order-by-type': 'false',
    },
    'lint.pep8-naming': {
        'ignore-names': """\
["setUp",
    "tearDown",
    "setUpClass",
    "tearDownClass",
    "setUpModule",
    "tearDownModule",
    "asyncSetUp",
    "asyncTearDown",
    "setUpTestData",
    "failureException",
    "longMessage",
    "maxDiff",
    "getLogger"]""",
    },
    'lint.pycodestyle': {
        'max-doc-length': '110',
    },
}

RULES_DESCRIPTIONS = {
    'B005': 'Using .strip() with multi-character strings is misleading',
    'D100': 'Missing docstring in public module',
    'D104': 'Missing docstring in public package',
    'D105': 'Missing docstring in magic method',
    'D107': 'Missing docstring in `__init__`',
    'D200': 'One-line docstring should fit on one line',
    'D203': '1 blank line required before class docstring',
    'D212': 'Multi-line docstring summary should start at the first line',
    'RUF012': 'Mutable class attributes should be annotated with `typing.ClassVar`',
    'S101': 'Use of `assert` detected',
    'TC001': 'Move application import into a type-checking block',
    'TC002': 'Move third-party import into a type-checking block',
    'TC003': 'Move standard library import into a type-checking block',
    'PYI041': 'Use `float` instead of `int | float`',
    'PT': 'flake8-pytest-style',
    'SLF001': 'Private member accessed',
    'FBT001': 'Boolean-typed positional argument in function definition',
    'PLR0913': 'Too many arguments to function call',
    'RUF018': 'Avoid assignment expressions in `assert` statements',
    'ANN': 'flake8-annotations',
    'D101': 'Missing docstring in public class',
    'D102': 'Missing docstring in public method',
    'D103': 'Missing docstring in public function',
    'B011': '[*] Do not `assert False` (`python -O` removes these calls), raise `AssertionError()`',
    'PLR2004': 'Magic value used in comparison',
}
