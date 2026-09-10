---
name: safe_refactoring
purpose: Refactoring rules that preserve behavior and minimize risk.
category: refactoring
triggers:
  - refactor
  - safe
  - test
  - incremental
  - behavior
dependencies: []
related: []
priority: supporting
estimated_tokens: 1137
---
# Refactoring: Safe Refactoring

**Purpose**: Refactoring rules that preserve behavior and minimize risk.

**When to use**: Any code restructuring, cleanup, or improvement.

---

## Core Rules

### Refactoring Principles
1. **Tests first** — No refactoring without tests
2. **Small steps** — One change at a time
3. **Run tests after each step** — Verify immediately
4. **Preserve behavior** — No functional changes
5. **Commit often** — Easy rollback
6. **Guard clauses first** — Reduce nesting before extracting
7. **Extract to protocol** — Depend on abstractions, not concretions

### Refactoring Workflow
```
1. RUN TESTS (baseline)
2. IDENTIFY refactoring goal
3. MAKE SMALLEST CHANGE
4. RUN TESTS
5. REPEAT 3-4 until goal achieved
6. RUN FULL TEST SUITE
7. REVIEW DIFF
```

### Safe Refactoring Patterns

#### Extract Function
```python
# Before
def process_order(order):
    validate(order)
    total = calculate_total(order.items)
    tax = total * TAX_RATE
    final = total + tax
    save_order(order, final)
    send_confirmation(order)

# After — extract calculation
def calculate_final_total(items):
    total = calculate_total(items)
    tax = total * TAX_RATE
    return total + tax

def process_order(order):
    validate(order)
    final = calculate_final_total(order.items)
    save_order(order, final)
    send_confirmation(order)
```

#### Extract Class (God Class Decomposition)
```python
# Before — God class with multiple responsibilities
class OrderService:
    def process(self, order):
        self.validate(order)
        self.calculate_pricing(order)
        self.save(order)
        self.notify(order)
        self.generate_report(order)  # Unrelated!
        self.sync_inventory(order)   # Unrelated!

# After — Separate concerns (Single Responsibility)
class OrderValidator:
    def validate(self, order): ...

class PricingCalculator:
    def calculate(self, order): ...

class OrderRepository:
    def save(self, order): ...

class NotificationService:
    def notify(self, order): ...

class ReportGenerator:          # Extracted: unrelated concern
    def generate(self, order): ...

class InventorySync:            # Extracted: unrelated concern
    def sync(self, order): ...

class OrderService:
    def __init__(self, validator, calculator, repo, notifier, reporter, inventory):
        self.validator = validator
        self.calculator = calculator
        self.repo = repo
        self.notifier = notifier
        self.reporter = reporter
        self.inventory = inventory
    
    def process(self, order):
        self.validator.validate(order)
        self.calculator.calculate(order)
        self.repo.save(order)
        self.notifier.notify(order)
        # Reporter and inventory called by caller if needed
```

#### Replace Conditional with Polymorphism
```python
# Before
def process_payment(payment):
    if payment.type == "credit":
        process_credit(payment)
    elif payment.type == "debit":
        process_debit(payment)
    elif payment.type == "paypal":
        process_paypal(payment)

# After
class PaymentProcessor(Protocol):
    def process(self, payment): ...

class CreditProcessor:
    def process(self, payment): ...

class DebitProcessor:
    def process(self, payment): ...

class PayPalProcessor:
    def process(self, payment): ...

PROCESSORS = {
    "credit": CreditProcessor(),
    "debit": DebitProcessor(),
    "paypal": PayPalProcessor(),
}

def process_payment(payment):
    PROCESSORS[payment.type].process(payment)
```

#### Introduce Parameter Object (Config Object)
```python
# Before — too many parameters
def create_user(email, name, age, address, phone, preferences, referral):
    ...

# After — config object
@dataclass
class UserData:
    email: str
    name: str
    age: int
    address: str
    phone: str
    preferences: dict
    referral: str | None = None

def create_user(data: UserData):
    ...
```

#### Guard Clauses (Reduce Nesting First)
```python
# Before — deeply nested
def process_user(user):
    if user.active:
        if user.has_permission("write"):
            data = fetch_data(user)
            return transform(data)
        else:
            return Result.error("forbidden")
    else:
        return Result.error("inactive")

# After — guard clauses, flat structure
def process_user(user):
    if not user.active:
        return Result.error("inactive")
    
    if not user.has_permission("write"):
        return Result.error("forbidden")
    
    # Main logic at base indent
    data = fetch_data(user)
    return Result.ok(transform(data))
```

---

### Production Gotchas

| Gotcha | Symptom | Fix |
|--------|---------|-----|
| No tests | Behavior changes silently | Write tests FIRST (characterization tests if legacy) |
| Extracting too much | New abstractions leak, over-engineered | Wait for 3rd use case (Rule of Three) |
| God class not fully split | Remaining methods still coupled | Extract ALL unrelated concerns |
| Missing guard clauses | Deep nesting persists | Add guard clauses BEFORE extracting |
| No feature flag | Can't rollback in production | Add feature flag for risky changes |
| Performance regression | Slower after "cleanup" | Benchmark before/after |
| Implicit behavior change | Tests pass but behavior differs | Property-based tests, snapshot tests |

---

### Verification

```python
# Characterization tests (for legacy code without tests)
def test_legacy_behavior():
    """Capture current behavior before refactoring."""
    # Test with real inputs, record outputs
    assert legacy_process(input_a) == expected_a
    assert legacy_process(input_b) == expected_b

# Property-based testing for refactoring
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_refactored_sort_preserves_elements(items):
    """Refactored sort must preserve all elements."""
    original = items[:]
    refactored_sort(items)
    assert sorted(original) == sorted(items)

# Snapshot testing for complex outputs
def test_report_generation_snapshot(snapshot):
    """Refactored report must match previous output."""
    result = generate_report(sample_data)
    assert result == snapshot

# Contract testing for extracted interfaces
def test_repository_contract(repo: OrderRepository):
    """Any implementation must satisfy contract."""
    order = repo.save(sample_order)
    assert repo.get(order.id) == order
    assert repo.get(999999) is None
```

---

## Decision Rules

| Refactoring | When Safe |
|-------------|-----------|
| Extract function | Pure logic, well-tested |
| Extract class | Clear responsibility boundary |
| Rename | IDE refactoring, all references updated |
| Move method | No behavior change |
| Replace conditional | Open/closed principle needed |
| Introduce parameter object | >4 related parameters |

---

## Preferred Patterns

```python
# Strangler Fig for large refactors
# 1. Create new implementation alongside old
# 2. Route new calls to new implementation
# 3. Migrate callers one by one
# 4. Remove old implementation

# Feature flag for safe rollout
def process_order(order):
    if settings.use_new_pricing:
        return new_pricing.calculate(order)
    return old_pricing.calculate(order)
```

---

## Avoid

- Refactoring without tests
- Multiple changes in one step
- "While I'm here" changes
- Changing behavior during refactor
- Big bang refactoring
- Refactoring working code unnecessarily

---

## Validation Considerations

- Tests pass at every step
- `git diff` shows only refactoring
- No behavior changes in diff
- Performance regression check
- Code review focused on structure

---

## Related Skills

- `refactoring/incremental.md`
- `refactoring/behavior_preservation.md`
- `testing/regression_tests.md`
- `testing/organization.md`