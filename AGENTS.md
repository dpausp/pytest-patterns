# pytest-patterns - Agent Guidelines

## Project Overview

pytest-patterns is a pytest plugin providing a pattern matching engine optimized
for testing complex string output (CLI output, HTML, logs, etc.).

## Build/Test Commands

```bash
# Run all tests
hatch run test

# Run single test file
hatch run test tests/test_basics.py

# Run single test function
hatch run test tests/test_basics.py::test_tab_replace

# Run with verbose output
hatch run test tests -vv

# Run examples (intentionally fail to show reporting)
hatch run test examples -vv

# Run with coverage
hatch run test --cov
```

## Linting/Formatting Commands

```bash
# Format code (black + ruff --fix)
hatch run fmt

# Check style only (no changes)
hatch run style

# Type checking with mypy
hatch run typing

# Run all linting (style + typing)
hatch run all
```

## Development Setup

```bash
# Enter nix development shell (if using nix)
nix develop

# Install pre-commit hooks
pre-commit install
```

## Code Style Guidelines

### Line Length & Formatting

- **80 characters max line length** (strict)
- Use `black` for formatting with `skip-string-normalization = true`
- Use `ruff` for linting

### Python Version

- Target: Python 3.8+ (for typing features)
- Support: Python 3.7 through 3.12

### Imports

```python
# Standard library first (alphabetically)
from __future__ import annotations

import enum
import re
from typing import Any, Iterator

# Third-party next
import pytest

# Local imports last (absolute imports only, no relative)
from pytest_patterns.plugin import PatternsLib
```

- **Absolute imports only** - ban-relative-imports is enforced
- `from __future__ import annotations` at top for modern typing
- Group: stdlib → third-party → local

### Type Annotations

- **mypy strict mode** is enabled
- All functions must have type annotations
- Use modern typing syntax where appropriate:

```python
# Good
def match(pattern: str, line: str) -> bool | re.Match[str] | None:
    ...

def cursor(self) -> Iterator[Line]:
    ...

# Use class-level attributes with type hints
class Line:
    status: Status = Status.UNEXPECTED
    status_cause: str = ""
```

### Naming Conventions

- `snake_case` for functions, variables, methods
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Pattern names in tests are descriptive: `patterns.better_things`, `patterns.conclusio`

### Error Handling

- Let errors crash early and loud - no silent failures
- Use assertions for internal invariants
- Propagate exceptions rather than catching and hiding

### Docstrings

- Use triple-quoted strings for multi-line docstrings
- Keep them concise and factual

```python
def continuous(self, lines: str) -> None:
    """These lines must appear once and they must be continuous."""
    ...
```

## Project Structure

```
src/pytest_patterns/
    __init__.py          # Package init (empty)
    __about__.py         # Version info
    plugin.py            # Main plugin implementation

tests/
    test_basics.py       # Core functionality tests
    test_edge_cases.py   # Edge case tests

examples/
    test_examples.py     # Usage examples (intentionally fail)
```

## Ruff Rules (Key Ones)

The project enables extensive ruff rules. Key ones to remember:

- `A` - flake8-builtins (shadowing builtins)
- `B` - flake8-bugbear (common bugs)
- `C901` - mccabe complexity (ignored, but be reasonable)
- `E`/`W` - pycodestyle errors/warnings
- `F` - pyflakes
- `I` - isort
- `N` - pep8-naming
- `PLR` - pylint refactor
- `RUF` - ruff-specific rules
- `S` - bandit security (S101 ignored in tests)
- `UP` - pyupgrade

## Special Patterns in This Project

### Pattern Matching API

The plugin provides a `patterns` fixture:

```python
def test_something(patterns):
    p = patterns.my_pattern
    p.optional("...heartbeat...")      # Optional lines
    p.in_order("""line1\nline2""")      # Must appear in order
    p.continuous("""line1\nline2""")    # Must be continuous
    p.refused("...error...")            # Must NOT appear
    
    full = patterns.full
    full.merge("my_pattern", "other")   # Combine patterns
    assert full == some_string
```

### Wildcards

- `...` matches any characters (non-greedy): `"...error..."`
- `<empty-line>` matches literal empty lines

## Commit Guidelines

- Run `hatch run fmt` before committing
- Ensure `hatch run all` passes
- Keep commits focused and atomic
