# Quality: Duplication

**Purpose**: Remove meaningful duplication without creating unnecessary abstractions.

**When to use**: Refactoring, code review, applying DRY principle correctly.

---

## Core Rules

### Types of Duplication

| Type | Example | Action |
|------|---------|--------|
| **True duplication** | Same logic, same reason to change | Extract |
| **Accidental duplication** | Same code, different reasons to change | Keep separate |
| **Structural duplication** | Similar structure, different domain | Keep separate |

### True Duplication (Extract)
```python
# Before — same validation logic
def create_user(data):
    if not data.email or "@" not in data.email:
        raise ValueError("Invalid email")
    if not data.name or len(data.name) < 2:
        raise ValueError("Invalid name")
    return save_user(data)

def update_user(user_id, data):
    if not data.email or "@" not in data.email:
        raise ValueError("Invalid email")
    if not data.name or len(data.name) < 2:
        raise ValueError("Invalid name")
    return update_user(user_id, data)

# After — extract
def validate_user_data(data):
    if not data.email or "@" not in data.email:
        raise ValueError("Invalid email")
    if not data.name or len(data.name) < 2:
        raise ValueError("Invalid name")

def create_user(data):
    validate_user_data(data)
    return save_user(data)

def update_user(user_id, data):
    validate_user_data(data)
    return update_user(user_id, data)
```

### Accidental Duplication (Don't Extract)
```python
# User validation
def validate_user(user):
    if not user.email or "@" not in user.email:
        raise ValueError("Invalid email")
    if user.age < 13:
        raise ValueError("Too young")

# Product validation — LOOKS similar but DIFFERENT rules
def validate_product(product):
    if not product.sku:
        raise ValueError("SKU required")
    if product.price <= 0:
        raise ValueError("Price must be positive")

# DON'T extract "validate_required_fields" — different domains, different change reasons
```

### Rule of Three
- First time: Write code
- Second time: Note similarity, but don't extract yet
- Third time: Extract common abstraction

---

## Decision Rules

| Duplication Type | Action |
|------------------|--------|
| Same logic, same domain, same change reason | Extract |
| Similar structure, different domain | Keep separate |
| Similar structure, different change reasons | Keep separate |
| Boilerplate (imports, decorators) | Accept or use code gen |
| Test setup | Fixtures/helpers OK |

---

## Preferred Patterns

```python
# Extract to function with clear name
def validate_email(email: str) -> None:
    if not email or "@" not in email:
        raise ValidationError("email", "Invalid email format")

# Extract to protocol for behavioral duplication
class Validator(Protocol):
    def validate(self, data: Any) -> None: ...

# Use decorators for cross-cutting duplication
def validate_request(schema: type):
    def decorator(func):
        @wraps(func)
        def wrapper(request):
            data = schema.model_validate(request.json)
            return func(data)
        return wrapper
    return decorator
```

---

## Avoid

- Extracting "utility" functions used once
- Creating base classes for accidental duplication
- Parameterizing extracted function to handle differences (creates complexity)
- DRY obsession — "Duplication is far cheaper than the wrong abstraction" (Sandi Metz)

---

## Validation Considerations

- `flake8-duplicates` / `pylint` duplicate-code detection
- Manual review: "If I change X, do I need to change Y?"
- Test each extracted unit independently

---

## Related Skills

- `quality/abstractions.md`
- `quality/functions.md`
- `quality/maintainability.md`
- `refactoring/safe_refactoring.md`