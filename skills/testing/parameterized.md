# Testing: Parameterized Tests

**Purpose**: Run same test logic with multiple inputs.

**When to use**: Testing multiple cases, edge cases, boundary values.

---

## Core Rules

### Basic Parametrization
```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (0, 0),
    (-1, -2),
])
def test_double(input: int, expected: int):
    assert double(input) == expected
```

### Multiple Parameters
```python
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a: int, b: int, expected: int):
    assert add(a, b) == expected
```

### Parametrized Fixtures
```python
@pytest.fixture(params=[1, 2, 3, 10, 100])
def number(request):
    return request.param

def test_positive(number: int):
    assert number > 0

# Combined with test parametrization
@pytest.mark.parametrize("multiplier", [2, 3, 10])
def test_multiply(number: int, multiplier: int):
    assert number * multiplier > 0
```

### Parametrizing with IDs
```python
@pytest.mark.parametrize("email,valid", [
    pytest.param("test@example.com", True, id="valid-standard"),
    pytest.param("user+tag@domain.org", True, id="valid-plus-tag"),
    pytest.param("invalid", False, id="invalid-no-at"),
    pytest.param("@domain.com", False, id="invalid-no-local"),
    pytest.param("user@", False, id="invalid-no-domain"),
], ids=lambda x: x[1] and "valid" or "invalid")
def test_email_validation(email: str, valid: bool):
    assert is_valid_email(email) == valid
```

### Parametrizing Classes
```python
@pytest.mark.parametrize("storage_cls", [InMemoryStorage, RedisStorage, FileStorage])
class TestStorage:
    def test_save_and_load(self, storage_cls):
        storage = storage_cls()
        storage.save("key", "value")
        assert storage.load("key") == "value"
    
    def test_delete(self, storage_cls):
        storage = storage_cls()
        storage.save("key", "value")
        storage.delete("key")
        assert storage.load("key") is None
```

### Dynamic Parametrization
```python
def pytest_generate_tests(metafunc):
    """Hook for dynamic parametrization."""
    if "test_file" in metafunc.fixturenames:
        test_files = list(Path("test_data").glob("*.json"))
        metafunc.parametrize("test_file", test_files, ids=lambda p: p.stem)

def test_with_file(test_file: Path):
    data = json.loads(test_file.read_text())
    assert process(data) == data["expected"]
```

### Cartesian Product (Multiple Decorators)
```python
@pytest.mark.parametrize("os", ["linux", "windows", "macos"])
@pytest.mark.parametrize("python", ["3.10", "3.11", "3.12"])
def test_compatibility(os: str, python: str):
    # Runs 9 combinations
    assert is_compatible(os, python)
```

---

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| Few cases (<3) | Overhead without benefit | Write separate tests |
| Complex logic in parametrize | Hard to debug | Use fixtures |
| Unrelated tests together | Hard to maintain | Separate test functions |
| Exponential combinations | Slow suite, hard to read | Reduce combinations |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Too many combinations | Slow suite, hard to read | Reduce, use `ids` |
| Complex logic in parametrize | Hard to debug | Use fixtures instead |
| Missing `ids` | Unclear test output | Add descriptive IDs |
| Cartesian product explosion | 100s of tests | Reduce combinations |
| Parametrizing unrelated tests | Hard to maintain | Separate test functions |

### Anti-Pattern

```python
# NEVER: Too many combinations
@pytest.mark.parametrize("a", range(10))
@pytest.mark.parametrize("b", range(10))
@pytest.mark.parametrize("c", range(10))
def test_all(a, b, c):  # 1000 tests!
    ...

# NEVER: Complex logic in parametrize
@pytest.mark.parametrize("input", [
    complex_function_1(),
    complex_function_2(),
    # Hard to debug when this fails
])

# BETTER: Focused parametrize with IDs
@pytest.mark.parametrize("input,expected", [
    pytest.param("valid@example.com", True, id="valid-email"),
    pytest.param("invalid", False, id="no-at-sign"),
], ids=lambda x: x[1] and "valid" or "invalid")
def test_email_validation(input, expected):
    assert is_valid_email(input) == expected
```

| Situation | Pattern |
|-----------|---------|
| Few cases (<10) | Inline parametrize |
| Many cases / data-driven | External data + `pytest_generate_tests` |
| Cross-product | Multiple `@parametrize` |
| Fixture variation | Parametrized fixture |
| Different implementations | Parametrize class |

---

## Preferred Patterns

```python
# Boundary value testing
@pytest.mark.parametrize("value", [
    0,           # Minimum
    1,           # Just above min
    100,         # Typical
    999,         # Just below max
    1000,        # Maximum
    1001,        # Just above max (invalid)
])
def test_range_validation(value: int):
    if 0 <= value <= 1000:
        assert validate_range(value) == value
    else:
        with pytest.raises(ValidationError):
            validate_range(value)

# Error case parametrization
ERROR_CASES = [
    (ValidationError, "empty", {}),
    (ValidationError, "missing_field", {"name": "test"}),
    (ConflictError, "duplicate", {"name": "test", "email": "a@b.c"}),
]

@pytest.mark.parametrize("error_type,case_name,input_data", ERROR_CASES)
def test_create_user_errors(error_type, case_name, input_data):
    with pytest.raises(error_type):
        create_user(**input_data)
```

---

## Avoid

- Too many combinations (exponential explosion)
- Parametrizing unrelated tests together
- Complex logic in parametrization (use fixtures instead)
- Missing `ids` for readability in output

---

## Validation Considerations

- `pytest --collect-only` shows all generated tests
- `pytest -v` shows parametrized test names
- `pytest -k "valid"` filters by id/name
- Duration tracking for large parametrized suites

---

## Related Skills

- `testing/organization.md`
- `testing/fixtures_mocks.md`
- `testing/edge_cases.md`