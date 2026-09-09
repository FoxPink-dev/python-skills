# Refactoring: Interface Stability

**Purpose**: Maintain stable public APIs during refactoring.

**When to use**: Any change to public functions, classes, or module APIs.

---

## Core Rules

### Public API Definition
- Functions/classes in `__all__`
- Exported in package `__init__.py`
- Documented in public docs
- Used by external consumers

### Stability Principles
1. **Add, don't remove** — Add new parameters with defaults
2. **Deprecate gracefully** — Warn before removing
3. **Version bump** — Breaking changes = major version
4. **Migration path** — Provide upgrade guide

### Safe API Evolution

#### Adding Parameters
```python
# Before
def fetch_users(client, limit=100):
    ...

# After — add with default (backward compatible)
def fetch_users(client, limit=100, *, filter=None, sort=None):
    ...
```

#### Changing Return Type
```python
# BAD — breaks callers
def get_user(id) -> User:
    ...

def get_user(id) -> User | None:  # Breaking!
    ...

# GOOD — add new function
def get_user(id) -> User:
    ...

def get_user_or_none(id) -> User | None:
    ...

# Or use Result type
def get_user(id) -> Result[User, NotFoundError]:
    ...
```

#### Deprecation Pattern
```python
import warnings
from functools import wraps

def deprecated(reason: str, version: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated since {version}: {reason}",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@deprecated("Use fetch_users_v2()", "2.0")
def fetch_users(client, limit=100):
    ...

# Type stub for deprecated
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    def fetch_users(...) -> list[User]: ...
```

#### Removing Parameters
```python
# Step 1: Make optional with deprecation
def process(data, *, old_param=None, new_param=None):
    if old_param is not None:
        warnings.warn("old_param deprecated", DeprecationWarning)
        new_param = old_param
    # Use new_param

# Step 2: Remove after deprecation period (major version)
def process(data, *, new_param):
    ...
```

### Versioning
```toml
# pyproject.toml
[project]
version = "2.1.0"  # Semantic: MAJOR.MINOR.PATCH

# MAJOR: Breaking API changes
# MINOR: New features, backward compatible
# PATCH: Bug fixes, backward compatible
```

### Interface Testing
```python
# Test public API surface
def test_public_api_surface():
    """Ensure public API hasn't accidentally changed"""
    from mypackage import __all__
    
    expected = {
        "UserService",
        "User",
        "create_user",
        "get_user",
        "ValidationError",
    }
    assert set(__all__) == expected

# Test signatures
import inspect

def test_user_service_signatures():
    sig = inspect.signature(UserService.create)
    params = list(sig.parameters.keys())
    assert params == ["self", "data", "validate"]
```

---

## Decision Rules

| Change | Approach |
|--------|----------|
| New optional parameter | Add with default |
| New function | Add alongside old |
| Change return type | New function + deprecate old |
| Remove parameter | Deprecate → Major version remove |
| Change behavior | New function + deprecate old |
| Rename | Add alias + deprecate old |

---

## Preferred Patterns

```python
# Version-gated imports
# mypackage/__init__.py
__version__ = "2.1.0"

# V1 API (deprecated)
from .v1 import UserService as UserServiceV1
from .v1 import create_user as create_user_v1

# V2 API (current)
from .v2 import UserService
from .v2 import create_user

# Deprecated aliases
import warnings
warnings.warn(
    "UserServiceV1 is deprecated, use UserService",
    DeprecationWarning,
)
```

---

## Avoid

- Silent breaking changes
- Removing public API in patch/minor
- Changing exception types
- Modifying default behavior
- Breaking `__all__` without major version

---

## Validation Considerations

- `pytest --collect-only` shows API surface
- `pip install -e . && python -c "import mypackage"` works
- Downstream consumers tested (if possible)
- Changelog documents all API changes

---

## Related Skills

- `refactoring/safe_refactoring.md`
- `refactoring/behavior_preservation.md`
- `engineering/pyproject_toml.md`
- `engineering/packaging.md`