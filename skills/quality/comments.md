---
name: comments
purpose: When and how to comment code effectively.
category: quality
triggers:
  - comment
  - docstring
  - type-comment
  - inline
  - documentation
dependencies: []
related: []
priority: supporting
estimated_tokens: 1100
---
# Quality: Comments

**Purpose**: When and how to comment code effectively.

**When to use**: All code generation and review.

---

## Core Rules

### Comment Philosophy
- **Code explains WHAT** — Comments explain WHY
- **Good code > Good comments** — Refactor to make code self-explanatory
- **Outdated comments are worse than no comments** — They mislead

### When to Comment

```python
# GOOD — Why: business rule, not obvious
def calculate_tax(amount: Decimal, region: str) -> Decimal:
    # Region X has special 0% rate for orders > $1000 per local law
    if region == "X" and amount > 1000:
        return Decimal("0")
    return amount * TAX_RATES[region]

# GOOD — Why: workaround for external limitation
def fetch_data(url: str) -> Data:
    # API returns 500 on HEAD requests, use GET with Range header
    response = http.get(url, headers={"Range": "bytes=0-"})
    ...

# GOOD — Why: non-obvious algorithm choice
def sort_items(items: list[Item]) -> list[Item]:
    # Timsort stable sort preserves insertion order for equal keys
    # Required for consistent pagination
    return sorted(items, key=lambda x: (x.priority, x.created_at))

# BAD — Restates code
def get_user(user_id: int) -> User:
    # Get user by ID
    return db.query(User).filter_by(id=user_id).first()

# BAD — Obvious
x = x + 1  # Increment x
```

### Docstrings (Not Comments)
```python
# Module docstring
"""User management service.

Provides CRUD operations for users and authentication.
"""

# Class docstring
class UserService:
    """Manages user lifecycle and authentication.
    
    Handles user creation, validation, and session management.
    Uses UserRepository for persistence.
    """
    
    def create_user(self, data: UserData) -> User:
        """Create a new user.
        
        Args:
            data: Validated user data.
            
        Returns:
            Created user with assigned ID.
            
        Raises:
            ValidationError: If data is invalid.
            ConflictError: If email already exists.
        """
        ...
```

### Inline Comments (Rare)
```python
# Only for non-obvious logic
result = complex_calculation()  # type: ignore[assignment]  # mypy false positive

# Or algorithm explanation
# Use Fisher-Yates shuffle for uniform distribution
for i in range(len(items) - 1, 0, -1):
    j = random.randint(0, i)
    items[i], items[j] = items[j], items[i]
```

### TODO/FIXME Comments
```python
# Format: # TODO(author): description
# TODO(john): Add retry logic when API supports it

# FIXME: Known bug
# FIXME: Race condition on concurrent updates
```

### Commented Code
```python
# NEVER commit commented-out code
# def old_function():
#     ...
# Use version control history instead
```

---

## Decision Rules

| Situation | Comment? |
|-----------|----------|
| Non-obvious business logic | Yes (WHY) |
| Workaround for external issue | Yes (WHY) |
| Algorithm choice rationale | Yes (WHY) |
| Complex regex | Yes (pattern explanation) |
| Obvious code | No |
| Restating code | No |
| TODO without issue reference | No (use issue tracker) |

---

## Preferred Patterns

```python
# Docstring for public API
def process_payment(payment: Payment) -> PaymentResult:
    """Process a payment through the configured gateway.
    
    Handles validation, authorization, and capture.
    Retries on transient gateway errors (up to 3 attempts).
    
    Args:
        payment: Validated payment with amount and method.
        
    Returns:
        PaymentResult with transaction ID and status.
        
    Raises:
        PaymentError: If gateway rejects payment.
        GatewayUnavailable: If gateway is unreachable.
    """
    ...

# Inline only for genuinely tricky code
def hash_password(password: str) -> str:
    # Argon2id with memory=64MB, iterations=3, parallelism=4
    # Parameters per OWASP 2023 recommendations
    return argon2.hash(password)
```

---

## Avoid

- Commented-out code blocks
- Redundant comments (`i = i + 1  # increment`)
- Comments that can be replaced by better naming
- Comments explaining standard library usage
- Outdated comments (delete when code changes)

---

## Validation Considerations

- `ruff` checks for TODO/FIXME format
- Docstring coverage (`pydocstyle`, `interrogate`)
- No commented code in diffs

---

## Related Skills

- `quality/documentation.md`
- `quality/readability.md`
- `quality/naming.md`