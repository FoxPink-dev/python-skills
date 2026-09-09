# Quality: Readability

**Purpose**: Code should be easy for another developer to understand.

**When to use**: All code generation and review.
---
---
name: quality_readability
purpose: Code should be easy for another developer to understand
category: quality
triggers:
  - readability
  - cognitive load
  - nesting
  - line length
  - naming
  - guard clause
dependencies:
  - quality/naming.md
  - quality/functions.md
  - quality/abstractions.md
  - quality/comments.md
priority: primary
estimated_tokens: 1500
---

## Core Rules

### Cognitive Load
- Limit concepts per function
- Use meaningful names (see naming.md)
- Avoid clever tricks
- Prefer explicit over implicit

### Vertical Density
```python
# GOOD — spaced out
def process_user(user: User) -> Result:
    validate(user)
    
    enriched = enrich(user)
    
    saved = save(enriched)
    
    notify(saved)
    
    return Result.ok(saved)

# BAD — cramped
def process_user(user): validate(user); enriched=enrich(user); saved=save(enriched); notify(saved); return Result.ok(saved)
```

### Horizontal Density
```python
# GOOD — within line length
result = process(
    user=user,
    options=default_options,
    callback=on_complete,
)

# BAD — too wide
result = process(user=user, options=default_options, callback=on_complete, timeout=30, retry=True, validate=True)
```

### Line Length
- Target: 88-100 chars (configurable per project)
- Break long lines at logical points
- Use parentheses for implicit continuation

```python
# Good breaks
long_function_call(
    argument_one=value1,
    argument_two=value2,
    argument_three=value3,
)

# Dictionary
config = {
    "key_one": "value1",
    "key_two": "value2",
}

# Type hints
def func(
    arg1: VeryLongTypeName,
    arg2: AnotherVeryLongTypeName,
) -> ReturnTypeName:
    ...
```

### Blank Lines
- Between logical sections in function
- Between class methods
- Around top-level definitions (2 blank lines)

```python
def process(data: Data) -> Result:
    # Validation
    if not data.is_valid:
        return Result.error("invalid")
    
    # Transformation
    transformed = transform(data)
    
    # Persistence
    saved = save(transformed)
    
    return Result.ok(saved)
```

### Guard Clauses (Reduce Nesting)
```python
# GOOD — flat structure
def process(user: User) -> Result:
    if not user.active:
        return Result.error("inactive")
    
    if not user.has_permission("write"):
        return Result.error("forbidden")
    
    # Main logic at base indent
    data = fetch_data(user)
    return Result.ok(transform(data))

# BAD — deeply nested
def process(user: User) -> Result:
    if user.active:
        if user.has_permission("write"):
            data = fetch_data(user)
            return Result.ok(transform(data))
        else:
            return Result.error("forbidden")
    else:
        return Result.error("inactive")
```

### Named Intermediate Values
```python
# GOOD — self-documenting
def calculate_price(item: Item, user: User) -> Price:
    base_price = item.base_price
    discount = user.discount_rate
    tax_rate = get_tax_rate(user.region)
    
    discounted = base_price * (1 - discount)
    final = discounted * (1 + tax_rate)
    
    return Price(amount=final, currency=item.currency)

# BAD — magic calculations
def calculate_price(item: Item, user: User) -> Price:
    return Price(amount=item.base_price * (1 - user.discount_rate) * (1 + get_tax_rate(user.region)), currency=item.currency)
```

---

## Decision Rules

| Situation | Pattern |
|-----------|---------|
| Complex condition | Extract to variable/function |
| Long expression | Break across lines |
| Multiple operations | Separate with blank lines |
| Nested logic | Early return / guard clauses |
| Magic numbers | Named constants |
| Boolean flag controls behavior | Split into two functions |

---

## Preferred Patterns

```python
# Guard clauses (reduce nesting)
def process(user: User) -> Result:
    if not user.active:
        return Result.error("inactive")
    
    if not user.has_permission("write"):
        return Result.error("forbidden")
    
    # Main logic at base indent
    data = fetch_data(user)
    return Result.ok(transform(data))

# Named intermediate values
def calculate_price(item: Item, user: User) -> Price:
    base_price = item.base_price
    discount = user.discount_rate
    tax_rate = get_tax_rate(user.region)
    
    discounted = base_price * (1 - discount)
    final = discounted * (1 + tax_rate)
    
    return Price(amount=final, currency=item.currency)

# Extract complex conditions
def is_eligible(user: User) -> bool:
    has_active_sub = user.subscription and user.subscription.active
    within_trial = user.trial_end and user.trial_end > datetime.now()
    return has_active_sub or within_trial

def process(user: User) -> Result:
    if not is_eligible(user):
        return Result.error("not eligible")
    ...
```

---

## Avoid

- Single-letter variables (except loop counters: `i`, `j`, `k`)
- Abbreviations (`usr`, `cfg`, `msg` — use `user`, `config`, `message`)
- Deep nesting (>3 levels)
- Long functions (>50 lines)
- Multiple statements per line
- Clever one-liners that require mental parsing
- Single-letter type variables (`T`, `U`) without context
- Shadowing built-ins (`list`, `dict`, `str`, `type`, `id`)

---

## Validation Considerations

- Linter line-length checks (ruff: `line-length`)
- Cyclomatic complexity (radon, xenon)
- Code review readability assessment
- `ruff` rules: B007 (loop var in closure), B008 (func call in default)

---

## Related Skills

- `quality/naming.md`
- `quality/functions.md`
- `quality/abstractions.md`
- `quality/comments.md`