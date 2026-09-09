# Engineering: Virtual Environments

**Purpose**: Isolated Python environments for development and deployment.

**When to use**: All Python development. Never install packages globally.

## Core Rules

### Tool Selection
| Tool | Use Case |
|------|----------|
| `venv` (stdlib) | Simple, no dependencies |
| `virtualenv` | Faster, more features |
| `uv` | Fast, modern, replaces pip/venv |
| `poetry` | Full project management |
| `pdm` | PEP 621 native, good for libs |
| `hatch` | Environments + build + publish |
| `conda` | Data science, non-Python deps |

### Creating Environments
```bash
# uv (recommended - fast)
uv venv
uv venv --python 3.11
uv venv .venv --seed

# venv (stdlib)
python -m venv .venv
python3.11 -m venv .venv

# virtualenv
virtualenv .venv -p python3.11

# Activate
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows
```

### Dependency Installation
```bash
# uv (fastest)
uv pip install -e .           # Editable install
uv pip install -e ".[dev]"    # With optional deps
uv sync                       # From lock file

# pip
pip install -e .
pip install -e ".[dev]"

# From requirements.txt
uv pip install -r requirements.txt
pip install -r requirements.txt
```

### Lock Files
```bash
# uv
uv lock  # Creates uv.lock
uv sync  # Installs from lock file

# Or generate requirements.txt
uv pip compile requirements.in -o requirements.txt
uv pip compile requirements.in --extra dev -o requirements-dev.txt

# pip-tools
pip-compile requirements.in -o requirements.txt
pip-sync requirements.txt

# poetry
poetry lock
poetry install

# pdm
pdm lock
pdm install
```

### Environment Management
```bash
# uv - multiple environments
uv python install 3.10 3.11 3.12
uv venv --python 3.10 .venv310
uv venv --python 3.11 .venv311

# direnv (auto-activate)
# .envrc
layout uv
# or
layout python python3.11
```

### In Docker
```dockerfile
# Use uv for fast installs
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY src/ ./src/
RUN uv pip install --no-deps -e .

# Or simpler with pip
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
RUN pip install --no-cache-dir -e .
```

---

## Decision Rules

| Situation | Tool |
|-----------|------|
| New project, want speed | `uv` |
| Existing Poetry/PDM | Keep current |
| Simple script | `venv` |
| Data science | `conda` / `micromamba` |
| CI/CD | `uv` (fastest) |
| Multiple Python versions | `uv` + `direnv` |

---

## Preferred Patterns

```bash
# Project setup script (bin/setup or Makefile)
#!/bin/bash
set -euo pipefail

# Install uv if not present
if ! command -v uv &> /dev/null; then
    pipx install uv
fi

# Create venv and install
uv venv
uv sync --extra dev

# Install pre-commit
uv run pre-commit install

echo "Setup complete. Activate with: source .venv/bin/activate"
```

### pyproject.toml for uv
```toml
[tool.uv]
dev-dependencies = [
    "pytest>=7.4",
    "ruff>=0.5",
    "mypy>=1.10",
]
```

---

## Avoid

- Global package installation (`pip install package`)
- No virtual environment
- Committing `.venv/` to git
- Mixing package managers in one env
- Not using lock files for applications

---

## Validation Considerations

- `uv pip check` / `pip check` — no conflicts
- `uv pip list` — correct versions
- Reproducible: fresh env + lock file = same result
- CI uses same lock file

---

## Related Skills

- `engineering/dependency_management.md`
- `engineering/pyproject_toml.md`
- `engineering/packaging.md`
- `engineering/cli_apps.md`