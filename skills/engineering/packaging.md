---
name: packaging
purpose: Building and distributing Python packages.
category: engineering
triggers:
  - packaging
  - pyproject
  - wheel
  - sdist
  - build
  - publish
  - pypi
dependencies: []
related: []
priority: primary
estimated_tokens: 1000
---
# Engineering: Packaging

**Purpose**: Building and distributing Python packages.

**When to use**: Publishing to PyPI, creating wheels, Docker images.

## Core Rules

### Build Process
```bash
# Modern (PEP 517/518)
pipx run build
# or
python -m build

# Outputs:
# dist/
#   my_package-1.0.0.tar.gz    (source distribution)
#   my_package-1.0.0-py3-none-any.whl  (wheel)
```

### Wheel vs sdist
| Type | Contents | Use Case |
|------|----------|----------|
| Wheel (.whl) | Pre-compiled, metadata | Installation (fast) |
| sdist (.tar.gz) | Source code, pyproject.toml | Archival, source builds |

### Version Management
```toml
# pyproject.toml with hatchling
[tool.hatch.version]
source = "regex"
regex = '^__version__ = "(.+)"$'
path = "src/my_package/_version.py"
```

```python
# src/my_package/_version.py
__version__ = "1.2.3"
```

### Publishing to PyPI
```bash
# Test PyPI first
pipx run twine upload --repository testpypi dist/*

# Production
pipx run twine upload dist/*

# With API token (CI)
twine upload -u __token__ -p $PYPI_TOKEN dist/*
```

### Package Metadata Check
```bash
twine check dist/*
```

### PEP 561 (Typed Packages)
```toml
# pyproject.toml
[project]
# ... other config

# Include py.typed marker
[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]
# Or use setuptools:
# [tool.setuptools.package-data]
# "*" = ["py.typed"]
```

```bash
# Verify
pip install my-package
python -c "import my_package; print(my_package.__file__)"
# Should have py.typed in package root
```

---

## Decision Rules

| Goal | Tool |
|------|------|
| Build wheel/sdist | `build` (PEP 517) |
| Version management | `hatchling` / `setuptools-scm` |
| Publish to PyPI | `twine` |
| Docker image | Multi-stage build with `--target` |
| Monorepo | `hatch` environments or `pdm` |

---

## Docker Packaging

```dockerfile
# Multi-stage build
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --no-cache-dir build && python -m build --wheel

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /app/dist/*.whl ./
RUN pip install --no-cache-dir *.whl && rm *.whl
USER 1000
ENTRYPOINT ["my-cli"]
```

---

## Preferred Patterns

```toml
# Complete pyproject.toml for packaging
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
dependencies = [...]
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Typing :: Typed",  # PEP 561
]

[tool.hatch.version]
source = "regex"
regex = '^__version__ = "(.+)"$'
path = "src/my_package/_version.py"

[tool.hatch.build.targets.wheel]
packages = ["src/my_package"]
```

---

## Avoid

- `setup.py` for new projects
- Manual version updates in multiple files
- Publishing without `twine check`
- Missing `requires-python`
- No `Typing :: Typed` classifier for typed packages
- Committing `dist/` to git

---

## Validation Considerations

- `twine check dist/*` passes
- `pip install dist/*.whl` works
- Package imports correctly
- Version matches expected
- Metadata complete on PyPI

---

## Related Skills

- `engineering/pyproject_toml.md`
- `engineering/project_structure.md`
- `engineering/dependency_management.md`
- `engineering/virtual_environments.md`