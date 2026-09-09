---
name: core_functions
purpose: Python function definition, calling conventions, and patterns
category: core
triggers:
  - function
  - def
  - method
  - parameter
  - argument
  - callable
  - closure
  - decorator
dependencies:
  - core/advanced_python.md
  - generation/type_hints.md
  - quality/functions.md
  - anti_patterns/index.md
priority: primary
estimated_tokens: 2000
---
# Core: Functions

**Purpose**: Python function definition, calling conventions, and patterns.

**When to use**: Always active. Functions are the primary abstraction unit.

---

## Core Rules

### Definition
```python
def function_name(
    positional: type,
    positional_with_default: type = default,
    *args: type,
    keyword_only: type,
    keyword_only_with_default: type = default,
    **kwargs: type,
) -> return_type:
    """Docstring describing what, args, returns, raises."""
    ...
```

### Parameter Kinds (PEP 3102, PEP 570)
| Kind | Syntax | Position | Use For |
|------|--------|----------|---------|
| Positional-only | `pos_only, /` | Before `/` | API stability, `self`/`cls` |
| Positional-or-keyword | `pos_or_kw` | Default | Most parameters |
| Keyword-only | `*, kw_only` | After `*` | Required named args, clarity |
| Var-positional | `*args` | After positional | Variable positional args |
| Var-keyword | `**kwargs` | Last | Variable keyword args |

### Default Arguments
- Evaluated **once** at function definition time
- **Never use mutable defaults** (`[]`, `{}`, `set()`) — creates shared state
- Use `None` sentinel pattern instead

```python
# WRONG
def bad(items=[]):
    items.append(1)
    return items

# CORRECT
def good(items=None):
    if items is None:
        items = []
    items.append(1)
    return items
```

### Return Values
- Implicit `return None` if no return statement
- Multiple returns via tuple: `return a, b`
- Explicit `return` for early exits
- Type hint return type (`-> Type`)

### Function Attributes
```python
func.__name__        # Name
func.__doc__         # Docstring
func.__annotations__ # Type hints
func.__defaults__    # Default values tuple
func.__kwdefaults__  # Keyword-only defaults dict
```

---

## Calling Conventions

```python
# Positional
func(1, 2)

# Keyword
func(pos=1, kw=2)

# Mixed (positional before keyword)
func(1, kw=2)

# Unpacking
func(*args, **kwargs)
```

### Positional-Only Parameters (Python 3.8+)
```python
def func(pos_only, /, pos_or_kw, *, kw_only):
    ...
```
- Use `/` to enforce positional-only (e.g., `self`, `cls`, builtins like `len`)

---

## Advanced Patterns

### Closures
```python
def outer(x):
    def inner(y):
        return x + y  # Captures x from enclosing scope
    return inner

add5 = outer(5)
add5(3)  # 8
```
- Use `nonlocal` to modify captured variables

### Callable Objects
```python
class Adder:
    def __init__(self, n):
        self.n = n
    def __call__(self, x):
        return self.n + x

add5 = Adder(5)
add5(3)  # 8
```

### Decorators
```python
def decorator(func):
    @functools.wraps(func)  # Preserves metadata
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
def my_func():
    ...
```
- Always use `@functools.wraps` on wrapper functions
- Decorators execute at **definition time**

---

## Type Hints for Functions

```python
from typing import Callable, TypeVar

T = TypeVar('T')

def map_func(func: Callable[[int], T], values: list[int]) -> list[T]:
    return [func(v) for v in values]

# Overloads for complex signatures
from typing import overload

@overload
def func(x: int) -> int: ...
@overload
def func(x: str) -> str: ...
def func(x: int | str) -> int | str:
    return x
```

---

## Decision Rules

| Situation | Pattern |
|-----------|---------|
| Simple transformation | `def` + type hints |
| Need to capture state | Closure or callable class |
| Multiple related operations | Class with methods |
| Cross-cutting concerns | Decorator |
| Variable positional args | `*args` |
| Variable keyword args | `**kwargs` |
| API stability required | Positional-only (`/`) |
| Clarity for boolean flags | Keyword-only (`*`) |

---

## Preferred Patterns

```python
# Small, focused functions
def parse_date(s: str) -> datetime.date:
    return datetime.date.fromisoformat(s)

# Early returns for guard clauses
def process(user: User) -> Result:
    if not user.is_active:
        return Result.error("inactive")
    if not user.has_permission("read"):
        return Result.error("forbidden")
    return do_process(user)

# Keyword-only for clarity
def connect(host: str, port: int, *, timeout: float = 5.0, ssl: bool = True) -> Connection:
    ...
```

---

## Avoid

- Mutable default arguments (see anti-patterns)
- Functions with >7 parameters (use dataclass/config object)
- Deeply nested functions (limit closure depth)
- Decorators that change function signature unexpectedly
- `*args`/`**kwargs` without documentation of expected keys
- Modifying `**kwargs` in place (copy first)

---

## Validation Considerations

- Type checkers verify signatures and return types
- `inspect.signature()` for runtime introspection
- `functools.wraps` preserves signature for tooling

---

## Related Skills

- `generation/type_hints.md`
- `core/advanced_python.md` (decorators, closures)
- `anti_patterns/index.md` (mutable defaults)
- `quality/functions.md` (size, focus)
- `engineering/cli_apps.md` (CLI entry points)