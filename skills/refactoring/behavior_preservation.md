# Refactoring: Behavior Preservation

**Purpose**: Ensure refactoring doesn't change observable behavior.

**When to use**: Every refactoring, especially complex ones.

---

## Core Rules

### Behavior Definition
Behavior = **observable outputs for given inputs**
- Return values
- Side effects (DB writes, API calls, files, logs)
- Exceptions raised
- Timing (if specified in requirements)

### Preservation Techniques

#### 1. Characterization Tests (Golden Master)
```python
# Before refactoring, capture current behavior
def test_order_calculation_golden_master():
    """Characterization test - captures current behavior"""
    test_cases = [
        {"items": [{"price": 10, "qty": 2}], "tax_rate": 0.1},
        {"items": [{"price": 100, "qty": 1}], "tax_rate": 0.0},
        {"items": [], "tax_rate": 0.1},
        # ... 50+ real cases from production
    ]
    
    for case in test_cases:
        result = calculate_order_total(case["items"], case["tax_rate"])
        # Save as golden master
        assert result == case["expected"]
```

#### 2. Property-Based Tests
```python
from hypothesis import given, strategies as st

@given(st.lists(st.fixed_dictionaries({
    "price": st.integers(0, 10000),
    "qty": st.integers(1, 100),
})), st.floats(0, 0.5))
def test_calculation_properties(items, tax_rate):
    """Properties that must hold after refactoring"""
    result = calculate_order_total(items, tax_rate)
    
    # Property: total >= subtotal
    subtotal = sum(i["price"] * i["qty"] for i in items)
    assert result >= subtotal
    
    # Property: tax = subtotal * rate (approximately)
    expected_tax = subtotal * tax_rate
    actual_tax = result - subtotal
    assert abs(actual_tax - expected_tax) < 0.01
```

#### 3. Contract Tests
```python
# Protocol defines contract
class OrderCalculator(Protocol):
    def calculate(self, items: list[Item], tax_rate: float) -> Decimal: ...

# Both implementations must satisfy
@pytest.fixture(params=[LegacyCalculator, NewCalculator])
def calculator(request) -> OrderCalculator:
    return request.param()

def test_calculator_contract(calculator: OrderCalculator):
    # Same tests for both implementations
    result = calculator.calculate([Item(10, 2)], 0.1)
    assert result == Decimal("22.00")
```

#### 4. Parallel Run (Production)
```python
# Shadow mode - run both, compare, log differences
def process_order(order):
    legacy_result = legacy_processor.process(order)
    new_result = new_processor.process(order)
    
    if legacy_result != new_result:
        logger.warning(
            "Behavior mismatch",
            legacy=legacy_result,
            new=new_result,
            order_id=order.id,
        )
    
    return legacy_result  # Still return legacy during transition
```

### What Must Be Preserved
| Aspect | Verify |
|--------|--------|
| Return values | Exact equality (or specified tolerance) |
| Exceptions | Same type, message, context |
| Side effects | Same DB writes, API calls, files |
| Timing | Within acceptable bounds |
| Logs | Same level, structure (optional) |

---

## Decision Rules

| Refactor Type | Verification Method |
|---------------|---------------------|
| Simple extraction | Existing unit tests |
| Algorithm change | Property tests + golden master |
| Implementation swap | Contract tests + shadow mode |
| Large restructuring | Characterization tests + integration tests |

---

## Preferred Patterns

```python
# Regression test for every behavior change
def test_refactor_preserves_bug_fix_123():
    """Ensures refactoring doesn't reintroduce bug #123"""
    # Exact scenario from bug report
    input_data = create_bug_scenario()
    
    result = refactored_function(input_data)
    
    # Bug was: returned wrong value for edge case
    assert result == expected_correct_value
```

---

## Avoid

- Assuming "it's the same logic" without verification
- Deleting characterization tests after refactor
- Refactoring without any automated verification
- Changing behavior "while we're at it"

---

## Validation Considerations

- Run characterization tests before and after
- Property tests run on both implementations
- Shadow mode logs zero mismatches before cutover
- Integration tests cover full workflows

---

## Related Skills

- `refactoring/safe_refactoring.md`
- `refactoring/incremental.md`
- `testing/regression_tests.md`
- `testing/edge_cases.md`