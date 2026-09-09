# Quality: Naming

**Purpose**: Meaningful, consistent naming conventions.

**When to use**: All code generation. Names are the first documentation.

---

## Core Rules

### Naming Conventions (PEP 8)
| Type | Convention | Example |
|------|------------|---------|
| Module | lowercase, short | `utils`, `http_client` |
| Package | lowercase, short | `mypackage`, `api_client` |
| Class | PascalCase | `UserService`, `HTTPClient` |
| Function | snake_case | `get_user`, `process_order` |
| Method | snake_case | `save`, `validate` |
| Constant | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Variable | snake_case | `user_count`, `is_active` |
| Type variable | PascalCase | `T`, `UserT`, `KeyT` |
| Exception | PascalCase + Error/Exception | `ValidationError`, `NotFoundError` |

### Descriptive Names
```python
# GOOD
user_count = len(users)
max_retry_attempts = 3
is_user_active = user.status == "active"
process_payment(payment)

# BAD
n = len(users)
m = 3
flag = user.status == "active"
proc(p)
```

### Boolean Names
```python
# GOOD — positive, question form
is_active = True
has_permission = False
can_edit = True
should_retry = True

# BAD
not_inactive = True
no_permission = False
active = True  # Ambiguous: noun or adj?
```

### Collection Names
```python
# GOOD — plural for collections
users = get_users()
active_users = [u for u in users if u.is_active]
user_by_id = {u.id: u for u in users}

# BAD
user_list = get_users()
user_dict = {u.id: u for u in users}
```

### Function Names
```python
# GOOD — verb phrase
get_user(user_id)
create_user(data)
validate_email(email)
calculate_total(items)
save_to_database(record)

# BAD
user(user_id)        # Noun
user_create(data)    # Verb-noun reversed
check(email)         # Vague
total(items)         # Noun
persist(record)      # Too generic
```

### Class Names
```python
# GOOD — noun phrase
class UserService:
class PaymentProcessor:
class DatabaseConnection:
class HTTPClient:
class ValidationError:

# BAD
class UserManager:      # "Manager" is vague
class Utils:            # Namespace, not class
class Data:             # Too generic
class HandleUser:       # Verb phrase
```

### Module Names
```python
# GOOD
http_client.py
user_service.py
payment_processor.py

# BAD
client.py          # Too generic
user.py            # Conflicts with class User
service.py         # Vague
```

---

## Decision Rules

| Context | Convention |
|---------|------------|
| Public API | Full descriptive names |
| Internal helper | Can be shorter if context clear |
| Loop variable | `i`, `j`, `k` or `idx` |
| Comprehension | `x`, `item`, `elem` |
| Type variable | `T`, `K`, `V`, `T_co` |
| Private | Leading `_` (`_internal`) |
| Dunder | `__special__` (Python reserved) |

---

## Preferred Patterns

```python
# Consistent prefixes for related functions
def fetch_user(user_id: int) -> User:
def fetch_users(filters: UserFilters) -> list[User]:
def fetch_user_by_email(email: str) -> User | None:

# Consistent suffixes for related classes
class UserRepository:
class OrderRepository:
class ProductRepository:

# Clear boolean naming
if user.can_access(resource):
if config.should_retry_on_failure:
if not order.is_cancelled:
```

---

## Avoid

- Single letters (except loops/math)
- Abbreviations (`cfg`, `msg`, `usr`, `tmp`)
- Hungarian notation (`str_name`, `int_count`)
- Redundant prefixes (`my_`, `the_`, `obj_`)
- Name shadowing (`list = [...]`, `dict = {}`)
- Similar names differing only by case (`user` vs `User`)

---

## Validation Considerations

- Linter naming checks (`ruff` N800 series)
- `pylint` naming conventions
- Code review for clarity

---

## Related Skills

- `quality/readability.md`
- `quality/functions.md`
- `core/variables_types.md`