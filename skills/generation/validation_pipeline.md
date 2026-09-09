# Generation: Validation Pipeline

**Purpose**: Concrete validation process for generated code.

**When to use**: After every code generation or modification.
---
---
name: generation_validation_pipeline
purpose: Concrete validation process for generated code
category: generation
triggers:
  - validation
  - pipeline
  - verification
  - testing
  - linting
  - type checking
dependencies:
  - generation/workflow.md
  - generation/type_hints.md
  - generation/error_handling.md
  - testing/organization.md
  - engineering/pyproject_toml.md
  - security/dependency_risks.md
priority: primary
estimated_tokens: 2000
---

## Validation Steps (In Order)

### 1. Syntax Check
```bash
python -m py_compile file.py
# or
python -m py_compile module/
```
- Catches syntax errors, indentation errors
- Fast, runs on single file or directory

### 2. Type Checking
```bash
# Detect tool from pyproject.toml
mypy file.py
# or
pyright file.py
# or
pytype file.py
```
- Catches type mismatches, missing annotations
- Use project's config (`[tool.mypy]`, `pyrightconfig.json`)
- `--strict` for new code

### 3. Linting
```bash
ruff check file.py
# or
flake8 file.py
# or
pylint file.py
```
- Catches style issues, potential bugs, complexity
- Use project's config (`ruff.toml`, `.flake8`, `setup.cfg`)

### 4. Formatting Check
```bash
ruff format --check file.py
# or
black --check file.py
```
- Ensures consistent formatting
- Run formatter if check fails: `ruff format file.py`

### 5. Tests
```bash
# Detect test framework
pytest path/to/tests -v
# or
python -m pytest
# or
tox
```
- Run relevant tests (changed files + related)
- Full suite for significant changes

### 6. Relevant Execution
```bash
# Run the actual code if possible
python -m module arg1 arg2
# or
python script.py
```
- Smoke test the functionality
- Verify integration works

### 7. Security Scan (Optional)
```bash
bandit -r file.py
# or
safety check
```
- Security linting
- Dependency vulnerability check

---

## Project Tool Detection

Check for config files in project root:
```bash
ls pyproject.toml setup.cfg tox.ini ruff.toml .pre-commit-config.yaml pyrightconfig.json
```

| File | Tools |
|------|-------|
| `pyproject.toml` | `[tool.mypy]`, `[tool.ruff]`, `[tool.black]`, `[tool.pytest]`, `[tool.bandit]` |
| `ruff.toml` | Ruff config |
| `pyrightconfig.json` | Pyright config |
| `setup.cfg` | `[flake8]`, `[mypy]`, `[tool:pytest]` |
| `tox.ini` | Test environments |
| `.pre-commit-config.yaml` | Pre-commit hooks |

---

## Never Claim Without Evidence

| Claim | Required Evidence |
|-------|-------------------|
| "tested" | Test output showing pass |
| "verified" | Validation pipeline output |
| "linted" | Linter output (clean) |
| "type-safe" | Type checker output (clean) |
| "production-ready" | All above + security scan |
| "fixed" | Reproduction + fix + regression test |

---

## Validation Script Template

```python
#!/usr/bin/env python3
"""Validation pipeline for generated code."""
import subprocess
import sys
from pathlib import Path

def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

def check_syntax(path: Path) -> bool:
    result = run([sys.executable, "-m", "py_compile", str(path)])
    if result.returncode != 0:
        print(f"Syntax error: {result.stderr}")
        return False
    return True

def check_types(path: Path, config: Path) -> bool:
    # Detect mypy/pyright
    if (config / "pyproject.toml").exists():
        # Check for mypy config
        result = run(["mypy", str(path)])
        if result.returncode != 0:
            print(f"Type errors: {result.stdout}")
            return False
    return True

def check_lint(path: Path) -> bool:
    result = run(["ruff", "check", str(path)])
    if result.returncode != 0:
        print(f"Lint errors: {result.stdout}")
        return False
    return True

def check_format(path: Path) -> bool:
    result = run(["ruff", "format", "--check", str(path)])
    if result.returncode != 0:
        print(f"Format issues: {result.stdout}")
        return False
    return True

def run_tests(path: Path) -> bool:
    result = run(["pytest", str(path), "-v"])
    if result.returncode != 0:
        print(f"Test failures: {result.stdout}")
        return False
    return True

def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    all_pass = True
    
    all_pass &= check_syntax(target)
    all_pass &= check_types(target, target.parent)
    all_pass &= check_lint(target)
    all_pass &= check_format(target)
    all_pass &= run_tests(target)
    
    if all_pass:
        print("✓ All validation checks passed")
        sys.exit(0)
    else:
        print("✗ Validation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## Integration with Workflow

```
IMPLEMENT
    ↓
REVIEW (manual)
    ↓
VALIDATE (automated — run pipeline)
    ↓
FIX (if any step fails)
    ↓
RE-VALIDATE
    ↓
FINALIZE
```

**Do not skip validation steps.** Each step catches different issues.

---

## Decision Rules

| Situation | Validation Level |
|-----------|------------------|
| New module/file | Full pipeline (all 7 steps) |
| Bug fix | Syntax + Type + Lint + Tests + Security |
| Refactoring | Syntax + Type + Lint + Tests |
| Documentation only | Syntax + Lint |
| Config change | Syntax + Tests |

---

## Preferred Patterns

```bash
# Quick validation (syntax + lint + type)
python -m py_compile file.py && ruff check file.py && mypy file.py

# Full validation with tests
pytest path/to/tests -v --tb=short && mypy path/ && ruff check path/

# CI validation (all steps)
python -m py_compile src/ && mypy src/ && ruff check src/ && ruff format --check src/ && pytest tests/ && bandit -r src/
```

---

## Avoid

- Skipping validation steps (each catches different issues)
- Claiming "tested" without running tests
- Running only syntax check
- Not using project's configured tools
- Ignoring validation failures

---

## Related Skills

- `generation/workflow.md`
- `generation/type_hints.md`
- `generation/error_handling.md`
- `testing/organization.md`
- `engineering/pyproject_toml.md`
- `security/dependency_risks.md`