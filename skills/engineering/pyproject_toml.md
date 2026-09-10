---
name: pyproject_toml
purpose: Modern Python project configuration (PEP 621, 517, 518, 660).
category: engineering
triggers:
  - pyproject
  - toml
  - build-system
  - tool
  - metadata
dependencies: []
related: []
priority: primary
estimated_tokens: 1592
---
# Engineering: pyproject.toml

**Purpose**: Modern Python project configuration (PEP 621, 517, 518, 660).

**When to use**: All Python projects. Single source of truth for project metadata.

---

## Core Rules

### Minimal Structure
```toml
[project]
name = "my-package"
version = "1.0.0"
description = "Short description"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.31",
    "pydantic>=2.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.version]
source = "regex"
regex = '^__version__ = "(.+)"$'
path = "src/my_package/_version.py"
```

### Project Metadata (PEP 621)
```toml
[project]
name = "my-package"
version = "1.0.0"
description = "One-line description"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Author Name", email = "author@example.com"}
]
maintainers = [
    {name = "Maintainer", email = "maint@example.com"}
]
keywords = ["cli", "api", "utility"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
requires-python = ">=3.10"
dependencies = [
    "requests>=2.31,<3",
    "pydantic>=2.0,<3",
]
urls = {
    Homepage = "https://github.com/user/repo",
    Repository = "https://github.com/user/repo",
    Issues = "https://github.com/user/repo/issues",
    Documentation = "https://docs.example.com",
}
```

### Optional Dependencies
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "ruff>=0.1",
    "mypy>=1.0",
]
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]
docs = [
    "sphinx>=7.0",
    "furo>=2023",
]
async = [
    "aiohttp>=3.8",
]
```

### Dynamic Fields (Setuptools/Hatch)
```toml
[project]
dynamic = ["version", "description"]

[tool.hatch.metadata]
allow-direct-references = true

[tool.hatch.version]
source = "regex"
regex = '^__version__ = "(.+)"$'
path = "src/my_package/_version.py"
```

### Tool Configuration

#### Ruff (Linting + Formatting)
```toml
[tool.ruff]
target-version = "py310"
line-length = 100
select = [
    "E", "F", "I", "N", "UP", "W", "C4", "DTZ", "T10", "PTH", "S", "B", "A", "C", "Q", "TID", "RUF"
]
ignore = []
fixable = ["ALL"]
unfixable = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "lf"

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "D100", "D103"]
"src/**/__init__.py" = ["D104"]
```

#### MyPy (Type Checking)
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true
strict_optional = true
show_error_codes = true
namespace_packages = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

#### Pytest
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers --strict-config"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration",
    "unit: marks tests as unit",
]
filterwarnings = [
    "ignore::DeprecationWarning",
]
```

#### Coverage
```toml
[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "*/__main__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

#### Bandit (Security)
```toml
[tool.bandit]
exclude_dirs = ["tests", "docs"]
skips = ["B101", "B601"]  # assert, shell=True (if justified)
```

---

## Dependency Versioning

| Specifier | Meaning |
|-----------|---------|
| `>=1.0,<2` | Compatible release (preferred) |
| `~=1.0` | `>=1.0,==1.*` (compatible) |
| `==1.0.*` | Any 1.0.x |
| `>=1.0` | Minimum version (avoid upper bound) |
| `===1.0` | Exact version (rare) |

**Prefer**: `"package>=1.0,<2"` or `"package~=1.0"`

---

## Build Backends

| Backend | Config | Use Case |
|---------|--------|----------|
| `hatchling` | `[tool.hatch]` | Modern, fast, feature-rich |
| `setuptools` | `[tool.setuptools]` | Legacy compatibility |
| `flit` | `[tool.flit]` | Pure Python, simple |
| `pdm` | `[tool.pdm]` | PDM-managed projects |
| `poetry` | `[tool.poetry]` | Poetry-managed (legacy) |

---

## Decision Rules

| Need | Config |
|------|--------|
| Simple pure Python lib | `flit` or `hatchling` |
| Complex build (C extensions) | `setuptools` or `meson-python` |
| Monorepo | `hatch` with `[tool.hatch.envs]` |
| Existing Poetry/PDM | Keep current backend |
| New project | `hatchling` (recommended) |

---

## Preferred Patterns

```toml
# Complete example for typical project
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-package"
dynamic = ["version"]
description = "Description"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
dependencies = [
    "requests>=2.31,<3",
    "pydantic>=2.0,<3",
]
optional-dependencies = {
    dev = ["pytest", "ruff", "mypy", "pytest-asyncio"],
    test = ["pytest", "pytest-cov"],
}

[tool.hatch.version]
source = "regex"
regex = '^__version__ = "(.+)"$'
path = "src/my_package/_version.py"

[tool.ruff]
target-version = "py310"
line-length = 100

[tool.mypy]
python_version = "3.10"
strict = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

## Avoid

- `setup.py` / `setup.cfg` for new projects (legacy)
- Hardcoding version in multiple places
- Missing `requires-python`
- Overly restrictive upper bounds (`<2.0.0` instead of `<3`)
- No lock file for applications (use `pip-tools`, `uv`, `poetry.lock`, `pdm.lock`)

---

## Validation Considerations

- `pip install -e .` works
- `pipx run build` produces wheel
- `hatch version` shows correct version
- `mypy --config-file pyproject.toml` passes
- `ruff check --config pyproject.toml` passes

---

## Related Skills

- `engineering/project_structure.md`
- `engineering/dependency_management.md`
- `engineering/packaging.md`
- `engineering/virtual_environments.md`