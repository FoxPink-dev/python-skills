---
name: regression_tests
purpose: Prevent previously fixed bugs from reappearing
category: testing
triggers:
  - regression
  - bug
  - fix
  - golden
  - property
dependencies:
  - testing/organization
  - testing/edge_cases
  - refactoring/safe_refactoring
  - generation/error_handling
related:
  - testing/edge_cases
  - testing/parameterized
  - quality/abstractions
priority: high
estimated_tokens: 1500
---
# Testing: Regression Tests

**Purpose**: Prevent previously fixed bugs from reappearing.

**When to use**: Every bug fix, every behavior change, every refactoring.

---

## Core Rules

### Every Bug Fix = Regression Test
```python
# Bug: User creation failed with uppercase email
# Fix: Normalize email to lowercase

def test_user_creation_normalizes_email(user_service):
    """Regression: Issue #123 - uppercase email caused duplicate"""
    user = user_service.create("USER@EXAMPLE.COM", "Test")
    
    assert user.email == "user@example.com"
    
    # Duplicate should still fail
    with pytest.raises(ConflictError):
        user_service.create("user@example.com", "Test 2")
```

### Regression Test Naming
```python
def test_issue_123_email_normalization():
    ...

def test_cve_2024_xxxx_sql_injection_prevented():
    ...

def test_fix_memory_leak_in_batch_processor():
    ...

def test_regression_double_submit_idempotency():
    ...
```

### Test Location
```
tests/
├── regression/
│   ├── test_issue_123_email.py
│   ├── test_cve_2024_xxxx.py
│   └── test_pr_456_refactor.py
```

### Minimal Reproduction
```python
# Minimal test that reproduces the exact bug
def test_issue_456_truncated_unicode():
    """Regression: PR #456 - unicode truncation corrupted data"""
    # Exact input that caused bug
    input_data = "Hello \ud83d\ude00 World"  # Surrogate pair
    
    # Should handle gracefully, not corrupt
    result = process_text(input_data)
    
    # Verify no corruption
    assert "Hello" in result
    assert "World" in result
    # Original bug: result contained replacement chars or crashed
```

### Behavior Change Tests
```python
# When intentionally changing behavior
def test_new_email_validation_allows_plus_tags():
    """Behavior change: Issue #200 - allow plus tags in email"""
    # Old behavior: rejected
    # New behavior: accepts
    user = create_user("user+tag@example.com", "Test")
    assert user.email == "user+tag@example.com"

# Document the change
def test_old_email_validation_rejected_plus_tags():
    """Old behavior (for reference)"""
    # This test documents what USED to happen
    # Keep for history, mark as xfail
    import pytest
    pytest.xfail("Old behavior - plus tags now allowed")
    
    with pytest.raises(ValidationError):
        create_user("user+tag@example.com", "Test")
```

### Refactoring Regression
```python
# Before refactoring, capture behavior
def test_refactor_order_calculation_preserves_results():
    """Regression: Refactored OrderCalculator must produce identical results"""
    test_cases = load_golden_master("order_calculator_golden.json")
    
    for case in test_cases:
        result = OrderCalculator().calculate(case["input"])
        assert result == case["expected"], f"Failed on case: {case['name']}"
```

---

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| Deleting regression tests | Bug may reappear | Keep for history |
| Tests that don't reproduce bug | False confidence | Write minimal reproduction |
| Overly complex regression tests | Hard to maintain | Keep minimal |
| Regression test for every change | Noise, slow suite | Focus on bug fixes |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Deleting regression test | Bug reappears later | Keep test, mark as `@pytest.mark.regression` |
| Test doesn't reproduce bug | False confidence | Write exact reproduction case |
| Overly complex test | Hard to maintain | Keep minimal, focused |
| Missing bug reference | Can't trace origin | Include issue/PR number in docstring |
| Not running regression suite | Regressions slip through | CI must run regression tests |

### Anti-Pattern

```python
# NEVER: Delete regression test after fix
# def test_issue_123_fixed():  # DELETED - bug reappears!

# NEVER: Test that doesn't reproduce bug
def test_issue_123():
    result = process("normal input")  # Bug was with special input
    assert result == "expected"

# BETTER: Minimal reproduction
def test_issue_123_normalizes_email():
    """Regression: Issue #123 - uppercase email caused duplicate"""
    user = create_user("USER@EXAMPLE.COM")  # Exact trigger
    assert user.email == "user@example.com"
    with pytest.raises(ConflictError):
        create_user("user@example.com")  # Verify fix
```

| Trigger | Action |
|---------|--------|
| Bug reported | Write failing test, fix, test passes |
| Security issue | Write test for attack vector |
| Refactoring | Golden master tests / property tests |
| Behavior change | Test new behavior, document old |
| Dependency update | Test integration points |

---

## Preferred Patterns

```python
# Golden master for complex refactoring
def test_parser_golden_master():
    """Regression: Parser refactor must not change output"""
    inputs = load_test_inputs("parser_inputs.json")
    expected = load_expected_outputs("parser_expected.json")
    
    for inp, exp in zip(inputs, expected):
        result = parse(inp)
        assert result == exp, f"Mismatch for input: {inp}"

# Property test as regression
from hypothesis import given, strategies as st

@given(st.dictionaries(st.text(), st.integers()))
def test_config_merge_idempotent(config: dict):
    """Regression: Config merge should be idempotent"""
    merged_once = merge_configs(config, {})
    merged_twice = merge_configs(merged_once, {})
    assert merged_once == merged_twice
```

---

## Avoid

- Fixing bug without test
- Deleting regression tests ("it works now")
- Tests that don't actually reproduce the bug
- Refactoring without behavior verification

---

## Verification

- Every bug fix has a corresponding regression test
- Regression test name includes issue/PR number for traceability
- Regression test reproduces the exact trigger (not a simplified version)
- Run `pytest -m regression` to verify all regression tests pass
- Golden master files are version controlled and tested in CI
- CI pipeline fails if any regression test fails

---

## Related Skills

- `testing/organization.md`
- `testing/edge_cases.md`
- `refactoring/safe_refactoring.md`
- `generation/error_handling.md`