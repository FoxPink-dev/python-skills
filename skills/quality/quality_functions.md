# Quality: Functions

**Purpose**: Function design principles for maintainable code.

**When to use**: Writing or reviewing functions.

---
---
name: quality_functions
purpose: Function design principles for maintainable code
category: quality
triggers:
  - function
  - method
  - parameter
  - signature
  - complexity
  - cyclomatic
dependencies:
  - quality/readability.md
  - quality/maintainability.md
  - quality/abstractions.md
  - generation/error_handling.md
  - testing/organization.md
priority: primary
estimated_tokens: 1500
---

## Core Rules

### Size
- **Target**: < 30 lines (excluding docstrings)
- **Maximum**: 50 lines
- Split if exceeded

### Single Responsibility
- One logical operation per function
- Name describes what it does
- If "and" in name → split

### Parameters
- **Target**: ≤ 4 parameters
- **Maximum**: 7 parameters
- Use config object for more

```python
# BAD — too many params
def process(a, b, c, d, e, f, g, h):
    ...

# GOOD — config object
@dataclass
class ProcessConfig:
    a: int
    b: str
    c: float
    ...

def process(config: ProcessConfig):
    ...
```

### Return Values
- Single return type (union if needed)
- Early returns for guard clauses
- Explicit `return` at end (or implicit `None`)

```python
# GOOD — early returns
def find_user(users: list[User], id: int) -> User | None:
    if not users:
        return None
    
    for user in users:
        if user.id == id:
            return user
    
    return None

# BAD — nested
def find_user(users: list[User], id: int) -> User | None:
    result = None
    if users:
        for user in users:
            if user.id == id:
                result = user
                break
    return result
```

### Side Effects
- Document side effects in docstring
- Prefer pure functions (same input → same output)
- Separate pure logic from I/O

```python
# Pure
def calculate_total(items: list[Item]) -> Decimal:
    return sum(item.price for item in items)

# Impure (I/O) — separate
def save_order(order: Order) -> Order:
    db.save(order)
    return order
```

### Function Responsibility
- One logical operation per function
- Name describes what it does (verb + object: `validate_email`, `fetch_user`)
- If name contains "and" → split
- Each function should be testable in isolation

### Parameter Design
- **Positional-only** (`/`) for `self`, `cls`, or API stability
- **Keyword-only** (`*`) for boolean flags and optional config
- **Default values** must be immutable (use `None` sentinel)
- **Type hints** required for public API, optional for private helpers

```python
# GOOD — clear signature
def fetch_users(
    client: APIClient,
    filters: UserFilters | None = None,
    limit: int = 100,
    *,
    include_inactive: bool = False,
) -> list[User]:
    ...

# BAD — ambiguous
def fetch_users(client, filters=None, limit=100, include_inactive=False):
    ...
```

### Return Value Design
- Single return type (union if needed for errors)
- Early returns for guard clauses
- Explicit `return` at end (or implicit `None`)
- Use `Result` pattern for operations that can fail

```python
# GOOD — early returns, single type
def find_user(users: list[User], id: int) -> User | None:
    if not users:
        return None
    
    for user in users:
        if user.id == id:
            return user
    
    return None

# GOOD — Result pattern for fallible operations
def parse_user(data: dict) -> Result[User, ValidationError]:
    try:
        return Result.ok(User.model_validate(data))
    except ValidationError as e:
        return Result.err(e)
```

### Side Effects
- Document side effects in docstring (`"""Creates user and sends welcome email."""`)
- Prefer pure functions (same input → same output, no external mutation)
- Separate pure logic from I/O
- Pass dependencies explicitly, not via global state

```python
# Pure
def calculate_total(items: list[Item]) -> Decimal:
    return sum(item.price for item in items)

# Impure (I/O) — separate, inject dependencies
def save_order(order: Order, repo: OrderRepository) -> Order:
    repo.save(order)
    return order
```

---

## Decision Rules

| Situation | Pattern |
|-----------|---------|
| Repeated logic | Extract function |
| Complex condition | Extract predicate function |
| Multiple returns | Early returns |
| Many parameters | Config dataclass |
| Logic + I/O | Separate functions |
| Boolean flag controls behavior | Split into two functions |
| Output parameter (modify argument) | Return new value instead |
| Recursive without clear base case | Use iteration |

---

## Preferred Patterns

```python
# Composed from small functions
def process_order(order: Order) -> Result[Fulfillment, OrderError]:
    validate_order(order)
    payment = charge_payment(order)
    fulfillment = create_fulfillment(order)
    notify_customer(order, fulfillment)
    return Result.ok(fulfillment)

# Each small, testable
def validate_order(order: Order) -> None:
    if not order.items:
        raise ValidationError("items", "Order must have items")
    if order.total <= 0:
        raise ValidationError("total", "Total must be positive")
```

---

## Avoid

- Functions doing 3+ distinct things
- Boolean parameters controlling behavior (`process(data, True, False)`)
- Output parameters (modify argument)
- Global state modification
- Recursive functions without clear base case (use iteration)
- `*args`/`**kwargs` without documentation of expected keys
- Modifying `**kwargs` in place (copy first)
- Deeply nested functions (limit closure depth)

---

## Validation Considerations

- Cyclomatic complexity per function (< 10)
- Function length (lines) (< 50)
- Parameter count (≤ 7)
- Test coverage per function
- `ruff` rules: B006 (mutable default), B007 (loop var in closure), B008 (func call in default)

---

## Related Skills

- `quality/readability.md`
- `quality/maintainability.md`
- `quality/abstractions.md`
- `generation/error_handling.md`
- `testing/organization.md`