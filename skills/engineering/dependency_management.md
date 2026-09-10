---
name: dependency_management
purpose: Rules for adding, updating, and managing dependencies.
category: engineering
triggers:
  - dependency
  - pip
  - poetry
  - uv
  - requirements
  - lockfile
dependencies: []
related: []
priority: primary
estimated_tokens: 1460
---
# Engineering: Dependency Management

**Purpose**: Rules for adding, updating, and managing dependencies.

**When to use**: Any time a new import or requirement is considered.

---

## Core Rules

### Dependency Decision Tree
```
Can stdlib solve this?
    ↓ YES → Use stdlib
    ↓ NO
Is an existing project dependency suitable?
    ↓ YES → Use existing
    ↓ NO
Is a new dependency justified?
    ↓ YES → Add with justification
    ↓ NO → Reconsider approach
```

### Justification Criteria for New Dependencies
1. **Functionality gap** — stdlib + existing deps cannot reasonably solve
2. **Maintenance** — Actively maintained (recent releases, responsive issues)
3. **Security** — No known unpatched vulnerabilities
4. **Compatibility** — Supports project's Python version range
5. **License** — Compatible with project license
6. **Size** — Reasonable install size, minimal transitive deps
7. **Alternatives evaluated** — Considered lighter alternatives

### Version Constraints
```toml
# Libraries: compatible ranges
dependencies = [
    "requests>=2.31,<3",      # Semver major
    "pydantic>=2.0,<3",
    "click>=8.0,<9",
]

# Applications: lock files
# requirements.txt / uv.lock / poetry.lock / pdm.lock
```

### Dependency Categories
| Category | Purpose | Version Policy |
|----------|---------|----------------|
| Runtime | Required for library/app to work | Compatible range |
| Optional | Extra features | Compatible range |
| Dev | Testing, linting, docs | Pinned or loose |
| Build | Build backend, generators | Pinned |

---

## Lock Files (Applications)

### For Applications (Not Libraries)
```bash
# uv (fast, modern)
uv lock  # Creates uv.lock
uv sync  # Installs from lock file

# Or generate requirements.txt
uv pip compile requirements.in -o requirements.txt

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

### Lock File Policy
- **Libraries**: No lock file in repo (only `pyproject.toml`)
- **Applications**: Lock file committed (`requirements.txt`, `uv.lock`, `poetry.lock`)
- **CI**: Use lock file for reproducible builds

---

## Dependency Security

### Scanning
```bash
# Safety (checks known vulnerabilities)
safety check

# pip-audit
pip-audit

# GitHub Dependabot / GitLab Dependency Scanning
# Configured in CI
```

### Update Policy
```bash
# Check outdated
uv pip list --outdated
pip list --outdated

# Update (test first!)
uv pip install --upgrade package
# Run full test suite
```

---

## Vendoring (Last Resort)
```python
# Only when:
# - Dependency abandoned
# - Need modification
# - Cannot depend on external (air-gapped)

# Structure
src/
└── mypackage/
    ├── _vendor/
    │   └── requests/       # Copied source
    │       └── __init__.py # from _vendor.requests import ...
    └── ...
```

---

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| Vendoring as first choice | Maintenance burden | Use package manager |
| Pinning exact versions in libraries | Breaks user's dependency resolution | Use compatible ranges |
| Adding dep for single function | Dependency overhead | Copy code (with license) |
| No lock file for applications | Non-reproducible builds | Use lock file |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Adding dep for trivial functionality | Dependency bloat | Use stdlib or copy code |
| Pinning exact versions in libraries | Dependency conflicts | Use compatible ranges |
| No upper bounds | Breaking changes | Add upper bounds |
| Ignoring security advisories | Vulnerable code | Run `pip-audit` regularly |
| Transitive dependency hell | Conflicts, bloat | Audit with `pipdeptree` |

### Anti-Pattern

```python
# NEVER: Adding dep for single function
# Instead of: from dateutil import parser
# Use: datetime.fromisoformat() (Python 3.7+)

# NEVER: Pinning exact versions in library
# pyproject.toml
dependencies = ["requests==2.31.0"]  # Breaks user's deps

# BETTER: Compatible ranges
dependencies = ["requests>=2.31,<3"]
```

| Situation | Action |
|-----------|--------|
| Stdlib has it | Use stdlib |
| Existing dep has it | Use existing |
| Simple utility (few lines) | Copy code (with license) |
| Complex, well-maintained lib | Add dependency |
| Abandoned dependency | Fork/vendor or replace |
| Security vulnerability | Upgrade immediately |
| License conflict | Find alternative |

---

## Preferred Patterns

```toml
# pyproject.toml - clear separation
[project]
dependencies = [
    # Core runtime deps
    "httpx>=0.25,<1",
    "pydantic>=2.0,<3",
    "python-dotenv>=1.0,<2",
]

[project.optional-dependencies]
# Optional features
async = ["aiohttp>=3.8,<4"]
redis = ["redis>=5.0,<6"]
postgres = ["asyncpg>=0.29,<1", "sqlalchemy>=2.0,<3"]

# Dev tools (not installed by users)
dev = [
    "pytest>=7.4,<8",
    "pytest-asyncio>=0.21,<1",
    "pytest-cov>=4.1,<5",
    "ruff>=0.5,<1",
    "mypy>=1.10,<2",
    "pre-commit>=3.0,<4",
]

# Build deps (in build-system)
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## Avoid

- Adding deps for trivial functionality (`left-pad` style)
- Pinning exact versions in library `pyproject.toml` (`==1.2.3`)
- No upper bounds in library deps (breaking changes)
- Commiting `requirements.txt` for libraries
- Ignoring security advisories
- Transitive dependency hell (audit `pipdeptree`)

---

## Validation Considerations

- `pipdeptree` shows dependency graph
- `pip check` validates consistency
- `safety check` / `pip-audit` clean
- License check: `pip-licenses`
- Build reproducibility: `pip install` from lock file

---

## Related Skills

- `engineering/pyproject_toml.md`
- `engineering/packaging.md`
- `engineering/virtual_environments.md`
- `security/dependency_risks.md`