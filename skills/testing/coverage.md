# Testing: Coverage

**Purpose**: Meaningful test coverage measurement and targets.

**When to use**: Configuring coverage, interpreting reports, setting thresholds.

---

## Core Rules

### Coverage Types
| Type | Meaning |
|------|---------|
| **Line** | Executable lines executed |
| **Branch** | Decision branches taken (if/else, loops) |
| **Function** | Functions called |
| **Statement** | Similar to line |

### Configuration
```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = [
    "tests/*",
    "*/__main__.py",
    "*/migrations/*",
    "*/conftest.py",
]
branch = true  # Branch coverage (important!)

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
precision = 2
show_missing = true

[tool.coverage.html]
directory = "htmlcov"
```

### Running Coverage
```bash
# Basic
pytest --cov=mypackage --cov-report=term-missing

# With branch coverage
pytest --cov=mypackage --cov-branch --cov-report=term-missing

# HTML report
pytest --cov=mypackage --cov-report=html

# XML for CI
pytest --cov=mypackage --cov-report=xml
```

### Interpreting Coverage
```text
Name                    Stmts   Miss  Branch BrMiss  Cover   Missing
----------------------------------------------------------------------
src/mypackage/__init__      5      0      0      0   100%
src/mypackage/models.py    50      2     10      2    92%   45-46
src/mypackage/service.py   120     15     30      8    85%   78-85, 92-95
src/mypackage/utils.py     30      0      4      0   100%
----------------------------------------------------------------------
TOTAL                     205     17     44     10    90%
```

- **Line coverage**: 90% (188/205)
- **Branch coverage**: 77% (34/44) — more important!
- **Missing**: Shows exact lines/branches not covered

### Coverage Targets
| Project Type | Line | Branch |
|--------------|------|--------|
| New project | 90%+ | 85%+ |
| Mature library | 95%+ | 90%+ |
| Application | 80%+ | 75%+ |
| Legacy | Improve incrementally | |

### What Coverage Does NOT Measure
- **Logic correctness** — 100% coverage ≠ bug-free
- **Edge cases** — May cover line but not all values
- **Integration** — Unit coverage ≠ system works
- **Security** — Coverage doesn't check vulnerabilities

---

## Decision Rules

| Situation | Coverage Goal |
|-----------|---------------|
| New code (PR) | 100% line, 100% branch |
| Critical paths (auth, payments) | 100% branch |
| Legacy code | Incremental improvement |
| Generated code | Exclude (`pragma: no cover`) |
| Prototypes | No requirement |

---

## Preferred Patterns

```python
# Exclude from coverage (rare, justify)
def __repr__(self) -> str:  # pragma: no cover
    return f"<{self.__class__.__name__}(id={self.id})>"

# Hard to test error paths
def connect(self):  # pragma: no cover
    try:
        self._connect()
    except OSError as e:
        if e.errno == errno.ENETUNREACH:
            raise NetworkUnreachable() from e
        raise

# Branch coverage important here
def process(value: int) -> str:
    if value > 0:          # Branch 1
        return "positive"
    elif value < 0:        # Branch 2
        return "negative"
    else:                  # Branch 3
        return "zero"

# Test all 3 branches
@pytest.mark.parametrize("value,expected", [
    (1, "positive"),
    (-1, "negative"),
    (0, "zero"),
])
def test_process(value, expected):
    assert process(value) == expected
```

---

## Avoid

- Coverage as only quality metric
- 100% coverage mandate (leads to bad tests)
- Excluding code without justification
- Not measuring branch coverage
- Testing getters/setters just for coverage

---

## Validation Considerations

- CI fails if coverage drops below threshold
- `pytest --cov-branch --cov-fail-under=80` (single threshold for branch+line combined)
- Track coverage trends over time
- Focus on branch coverage for critical logic

---

## Related Skills

- `testing/organization.md`
- `testing/edge_cases.md`
- `testing/regression_tests.md`
- `quality/maintainability.md`