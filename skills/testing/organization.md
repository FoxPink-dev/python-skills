# Testing: Organization

**Purpose**: Structuring test suites for maintainability and speed.

**When to use**: Setting up or reorganizing test structure.

---

## Core Rules

### Directory Structure
```
tests/
├── conftest.py                 # Root fixtures
├── pytest.ini                  # Config (or pyproject.toml)
├── unit/                       # Fast, isolated
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/                # Real dependencies
│   ├── conftest.py
│   ├── test_database.py
│   ├── test_api.py
│   └── test_external.py
├── e2e/                        # Full stack (optional)
│   ├── conftest.py
│   └── test_flows.py
├── performance/                # Benchmarks (optional)
│   └── test_benchmarks.py
├── fixtures/                   # Shared test data
│   ├── sample_users.json
│   └── sample_orders.json
└── helpers/                    # Test utilities
    ├── __init__.py
    ├── builders.py
    └── matchers.py
```

### Naming Conventions
```
test_<module>.py                # Module tests
test_<class>.py                 # Class tests
test_<function>_<scenario>.py   # Specific scenario
Test<ClassName>                 # Test class
test_<function>_<condition>     # Test function
```

### Test Class Organization
```python
class TestUserService:
    """Tests for UserService."""
    
    class TestCreateUser:
        """Tests for create_user method."""
        
        def test_creates_user_with_valid_data(self):
            ...
        
        def test_raises_on_duplicate_email(self):
            ...
        
        def test_hashes_password(self):
            ...
    
    class TestGetUser:
        """Tests for get_user method."""
        
        def test_returns_user_when_exists(self):
            ...
        
        def test_returns_none_when_not_found(self):
            ...
```

### Marks for Categorization
```python
# pytest.ini
[tool.pytest.ini_options]
markers = [
    "unit: Fast, isolated tests",
    "integration: Tests with real dependencies",
    "e2e: Full system tests",
    "slow: Takes >1s",
    "requires_db: Needs database",
    "requires_network: Needs external API",
    "regression: Bug fix verification",
    "security: Security-related tests",
]

# Usage
@pytest.mark.unit
def test_unit():
    ...

@pytest.mark.integration
@pytest.mark.requires_db
def test_with_db():
    ...

# Run subsets
# pytest -m unit
# pytest -m "integration and not slow"
# pytest -m "not e2e"
```

### Configuration
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers --strict-config --tb=short"
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]
asyncio_mode = "auto"

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

---

## Decision Rules

| Test Type | Location | Markers | Speed Target |
|-----------|----------|---------|--------------|
| Unit | `tests/unit/` | `unit` | <100ms |
| Integration | `tests/integration/` | `integration`, `requires_db` | <1s |
| E2E | `tests/e2e/` | `e2e` | <30s |
| Regression | `tests/regression/` | `regression` | Varies |

---

## Preferred Patterns

```python
# Shared test utilities
# tests/helpers/builders.py
class UserBuilder:
    def __init__(self):
        self.data = {"email": "test@test.com", "name": "Test"}
    
    def with_email(self, email):
        self.data["email"] = email
        return self
    
    def build(self):
        return User(**self.data)

# tests/helpers/matchers.py
def assert_user_equal(actual: User, expected: User):
    assert actual.id == expected.id
    assert actual.email == expected.email
    assert actual.name == expected.name
    # Don't compare timestamps (flaky)

# Custom assertions
def assert_validation_error(exc_info, field: str, message_contains: str):
    assert exc_info.type is ValidationError
    assert exc_info.value.field == field
    assert message_contains in str(exc_info.value)
```

---

## Avoid

- All tests in one directory
- No markers (can't run subsets)
- Mixed unit/integration in same file
- Slow tests in unit suite
- Test order dependencies
- Duplicate fixtures across directories

---

## Validation Considerations

- `pytest --collect-only | head -20` shows structure
- `pytest --durations=10` shows slowest tests
- Coverage targets per test type
- CI runs unit on every PR, integration nightly

---

## Related Skills

- `testing/fixtures_mocks.md`
- `testing/parameterized.md`
- `engineering/virtual_environments.md`