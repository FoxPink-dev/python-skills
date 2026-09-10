---
name: edge_cases
purpose: Systematic edge case coverage for robust code
category: testing
triggers:
  - edge
  - boundary
  - parameter
  - hypothesis
  - fuzz
dependencies:
  - testing/organization
  - testing/parameterized
  - security/input_validation
  - generation/error_handling
related:
  - testing/parameterized
  - testing/regression_tests
  - security/input_validation
priority: high
estimated_tokens: 1500
---
# Testing: Edge Cases

**Purpose**: Systematic edge case coverage for robust code.

**When to use**: Writing tests for any function with external input or complex logic.

---

## Core Rules

### Edge Case Categories

| Category | Examples |
|----------|----------|
| **Empty/Zero** | `""`, `[]`, `{}`, `0`, `0.0`, `None` |
| **Boundary** | Min, max, min-1, max+1, off-by-one |
| **Special values** | `NaN`, `Inf`, `-0.0`, `True`/`False` as int |
| **Unicode** | Emoji, RTL, combining chars, null bytes |
| **Large** | Huge strings, deep nesting, many items |
| **Concurrent** | Race conditions, double-submit |
| **Failure** | Network error, timeout, disk full, permission denied |
| **Malformed** | Invalid encoding, truncated data, wrong type |

### Parameterized Edge Cases
```python
import pytest

# String edges
STRING_EDGES = [
    ("", "empty"),
    (" ", "whitespace"),
    ("\t\n\r", "control-chars"),
    ("a" * 10000, "long"),
    ("🎉🎊", "emoji"),
    ("\u200b", "zero-width"),
    ("\x00", "null-byte"),
    ("../../../etc/passwd", "traversal"),
]

@pytest.mark.parametrize("value,case_id", STRING_EDGES, ids=lambda x: x[1])
def test_string_input(value: str, case_id: str):
    result = process_string(value)
    assert isinstance(result, str)

# Numeric edges
NUMERIC_EDGES = [
    (0, "zero"),
    (-1, "negative"),
    (1, "positive"),
    (2**63 - 1, "max-int64"),
    (-(2**63), "min-int64"),
    (float("inf"), "infinity"),
    (float("-inf"), "neg-infinity"),
    (float("nan"), "nan"),
    (1.5, "float"),
]

@pytest.mark.parametrize("value,case_id", NUMERIC_EDGES, ids=lambda x: x[1])
def test_numeric_input(value, case_id):
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        with pytest.raises(ValidationError):
            process_number(value)
    else:
        result = process_number(value)
        assert result == expected(value)
```

### Collection Edges
```python
COLLECTION_EDGES = [
    ([], "empty"),
    ([1], "single"),
    ([1, 2], "two"),
    (list(range(10000)), "large"),
    ([None, "", 0, False], "falsy-values"),
    ([{"nested": {"deep": "value"}}], "nested"),
]

@pytest.mark.parametrize("items,case_id", COLLECTION_EDGES, ids=lambda x: x[1])
def test_collection_processing(items, case_id):
    result = process_items(items)
    assert len(result) == len(items)
```

### None/Optional Edges
```python
def test_optional_handling():
    # Explicit None
    assert process_optional(None) == default_value()
    
    # Missing key vs None value
    assert process_dict({}) == default_value()
    assert process_dict({"key": None}) == default_value()
    assert process_dict({"key": "value"}) == "value"
```

### Concurrency Edges
```python
import threading
import time

def test_thread_safety(counter):
    def increment():
        for _ in range(1000):
            counter.increment()
    
    threads = [threading.Thread(target=increment) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    assert counter.value == 10000  # No race condition
```

### Time Edges
```python
from freezegun import freeze_time

@freeze_time("2024-01-15 12:00:00")
def test_time_dependent():
    assert get_current_timestamp() == "2024-01-15T12:00:00Z"

# Leap year, DST, timezone
@freeze_time("2024-02-29 23:59:59")  # Leap day
def test_leap_year():
    ...

@freeze_time("2024-03-10 02:30:00", tz_offset=-5)  # DST transition
def test_dst():
    ...
```

---

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| Testing every possible value | Impractical, slow | Use hypothesis for property testing |
| Over-parameterized tests | Hard to read, slow | Focus on critical edges |
| Edge cases for trivial functions | Low ROI | Skip for simple utilities |
| Ignoring timezones | DST bugs, race conditions | Test timezone boundaries |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Only testing happy path | Bugs in edge cases | Systematic edge case checklist |
| Ignoring empty input | Crashes on `""`, `[]`, `{}` | Test empty collection/string |
| Ignoring Unicode | Encoding errors, crashes | Test emoji, RTL, combining chars |
| Ignoring concurrency | Race conditions, data corruption | Test thread safety |
| Ignoring timezones | DST bugs, offset errors | Test timezone boundaries |
| Missing off-by-one | Boundary errors | Test min, max, min-1, max+1 |

### Anti-Pattern

```python
# NEVER: Only test happy path
def test_process():
    result = process([1, 2, 3])
    assert result == [2, 4, 6]

# BETTER: Systematic edge cases
@pytest.mark.parametrize("input,expected", [
    ([], []),           # Empty
    ([1], [2]),         # Single
    ([1, 2, 3], [2, 4, 6]),  # Normal
    ([0, -1, 2], [0, -2, 4]),  # Zero/negative
])
def test_process_edges(input, expected):
    assert process(input) == expected
```

| Function Input | Edge Cases to Test |
|----------------|-------------------|
| String | Empty, whitespace, unicode, long, injection |
| Number | 0, negative, min/max, float special |
| List/Dict | Empty, single, large, nested, None elements |
| Optional | None, missing, empty string |
| Date/Time | Boundaries, DST, leap, timezone |
| File | Empty, large, missing, permission, symlink |
| Network | Timeout, 5xx, 4xx, malformed response |

---

## Preferred Patterns

```python
# Property-based testing (hypothesis)
from hypothesis import given, strategies as st

@given(st.text())
def test_string_property(s: str):
    # Should never crash on any string
    result = safe_process(s)
    assert isinstance(result, str)

@given(st.integers())
def test_int_property(n: int):
    result = process_int(n)
    assert result >= 0

@given(st.lists(st.integers()))
def test_list_property(items: list[int]):
    result = process_list(items)
    assert len(result) <= len(items)
```

---

## Avoid

- Only testing "happy path"
- Assuming input is always valid
- Missing boundary values (off-by-one)
- Not testing error handling paths
- Ignoring Unicode/timezone/concurrency

---

## Validation Considerations

- `pytest --cov` shows uncovered branches
- `hypothesis` finds unexpected edge cases
- Mutation testing (`mutmut`) verifies test quality
- Fuzzing for parsers/decoders

---

## Related Skills

- `testing/organization.md`
- `testing/parameterized.md`
- `testing/regression_tests.md`
- `security/input_validation.md`
- `generation/error_handling.md`