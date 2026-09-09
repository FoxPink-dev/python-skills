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

#### Extract Class
```python
# Before — mixed responsibilities
class OrderProcessor:
    def process(self, order):
        self.validate(order)
        self.calculate_pricing(order)
        self.save(order)
        self.notify(order)

# After — separate concerns
class OrderValidator:
    def validate(self, order): ...

class PricingCalculator:
    def calculate(self, order): ...

class OrderRepository:
    def save(self, order): ...

class NotificationService:
    def notify(self, order): ...

class OrderProcessor:
    def __init__(self, validator, calculator, repo, notifier):
        self.validator = validator
        self.calculator = calculator
        self.repo = repo
        self.notifier = notifier
    
    def process(self, order):
        self.validator.validate(order)
        self.calculator.calculate(order)
        self.repo.save(order)
        self.notifier.notify(order)
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

#### Introduce Parameter Object
```python
# Before
def create_user(email, name, age, address, phone, preferences, referral):
    ...

# After
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