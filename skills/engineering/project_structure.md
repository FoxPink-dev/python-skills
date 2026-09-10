---
name: project_structure
purpose: Modern Python project layout conventions.
category: engineering
triggers:
  - structure
  - layout
  - src-layout
  - monorepo
  - organization
dependencies: []
related: []
priority: primary
estimated_tokens: 1000
---
# Engineering: Project Structure

**Purpose**: Modern Python project layout conventions.

**When to use**: Creating new projects or understanding existing ones.

---

## Core Rules

### Recommended Layout (src-layout)
```
project-root/
├── pyproject.toml          # Project metadata, dependencies, tool config
├── README.md
├── LICENSE
├── src/
│   └── package_name/       # Actual package (matches distribution name)
│       ├── __init__.py
│       ├── _version.py     # Optional: version from setuptools-scm
│       ├── module.py
│       ├── subpackage/
│       │   ├── __init__.py
│       │   └── ...
│       └── py.typed        # Marker for PEP 561 (if typed)
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   ├── unit/
│   │   └── test_module.py
│   ├── integration/
│   └── fixtures/
├── docs/
├── scripts/                # Utility scripts
├── .github/
│   └── workflows/          # CI/CD
├── .gitignore
├── .pre-commit-config.yaml
└── docker/                 # Docker files (optional)
```

### Flat Layout (Simple Projects)
```
project-root/
├── pyproject.toml
├── package_name/
│   ├── __init__.py
│   └── ...
├── tests/
└── ...
```

### Key Principles

1. **src-layout preferred** — separates package from project config, prevents accidental imports
2. **Package name = distribution name** — `src/my_package` → `pip install my-package`
3. **Tests outside package** — `tests/` not `src/package/tests/`
4. **Single top-level package** — avoid multiple packages in one repo

---

## Module Organization

```
src/package/
├── __init__.py           # Public API exports
├── _internal.py          # Private (leading underscore)
├── core.py               # Core functionality
├── models.py             # Data models
├── services.py           # Business logic
├── api.py                # External interfaces
├── cli.py                # CLI entry point
├── config.py             # Configuration
├── exceptions.py         # Custom exceptions
└── utils.py              # Utilities (avoid if possible)
```

### `__init__.py` Pattern
```python
# src/package/__init__.py
"""Package docstring."""

from .core import main_function
from .models import User, Config
from .exceptions import PackageError

__version__ = "1.0.0"
__all__ = [
    "main_function",
    "User",
    "Config",
    "PackageError",
]
```

---

## Decision Rules

| Project Type | Layout |
|--------------|--------|
| Library (published to PyPI) | src-layout |
| Application (Docker, server) | src-layout or flat |
| Simple script | Flat (single file or package) |
| Monorepo (multiple packages) | `packages/pkg1/`, `packages/pkg2/` |

---

## Preferred Patterns

```python
# src/package/_version.py (for setuptools-scm)
# This file is generated at build time
__version__ = "0.0.0"

# src/package/__init__.py
try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0"

from .core import main
from .models import User

__all__ = ["main", "User", "__version__"]
```

---

## Avoid

- Multiple top-level packages in one distribution
- Putting tests inside the package
- `__init__.py` with heavy imports (slow import)
- Circular imports between modules
- Deep nesting (>3 levels)
- Non-package directories in `src/`

---

## Validation Considerations

- `pip install -e .` works correctly
- `python -m package` runs `__main__.py` if present
- Import time is fast
- `build` produces correct wheel

---

## Related Skills

- `engineering/pyproject_toml.md`
- `engineering/modules_packages.md`
- `engineering/packaging.md`
- `engineering/dependency_management.md`