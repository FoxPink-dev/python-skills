---
name: functools
purpose: Higher-order functions and function utilities.
category: stdlib
triggers:
  - functools
  - lru-cache
  - wraps
  - partial
  - reduce
  - singledispatch
dependencies: []
related: []
priority: supporting
estimated_tokens: 1431
---
# Stdlib: functools

**Purpose**: Higher-order functions and function utilities.

**When to use**: Function composition, caching, decoration, partial application.

---

## Core Rules

### `partial` / `partialmethod`
```python
from functools import partial, partialmethod

# Fix arguments
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
square(5)  # 25

# For methods (binds self)
class Math:
    def __init__(self, factor):
        self.factor = factor
    def multiply(self, x):
        return self.factor * x
    double = partialmethod(multiply, 2)
```

### `wraps` (Critical for Decorators)
```python
from functools import wraps

def my_decorator(func):
    @wraps(func)  # Copies __name__, __doc__, __annotations__, __module__, __qualname__, __dict__
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

- **Always** use on decorator wrappers
- Without it: lost metadata, broken introspection, broken type hints

### `lru_cache` (Memoization)
```python
from functools import lru_cache

@lru_cache(maxsize=128)  # None = unbounded
def fib(n: int) -> int:
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

fib.cache_info()   # CacheInfo(hits, misses, maxsize, currsize)
fib.cache_clear()  # Clear cache

# Typed cache (Python 3.9+)
@lru_cache(maxsize=None, typed=True)
def typed_func(x: int) -> int:  # Separate cache for int vs float
    ...
```

- Thread-safe
- Only for pure functions (same args → same result)
- `maxsize` should be power of 2 for performance

### `cache` (Python 3.9+)
```python
from functools import cache

@cache
def expensive(x):
    ...
```
- Unbounded `lru_cache` (no maxsize limit)
- Simpler for "cache forever" cases

### `cached_property` (Python 3.8+)
```python
from functools import cached_property

class DataProcessor:
    @cached_property
    def processed(self) -> DataFrame:
        return expensive_computation(self.raw)
```
- Computes once per instance, caches in `__dict__`
- Not thread-safe for simultaneous first access

### `singledispatch` / `singledispatchmethod`
```python
from functools import singledispatch, singledispatchmethod

@singledispatch
def serialize(obj):
    raise NotImplementedError(f"Cannot serialize {type(obj)}")

@serialize.register
def _(obj: int) -> str:
    return str(obj)

@serialize.register
def _(obj: list) -> str:
    return "[" + ", ".join(serialize(x) for x in obj) + "]"

# For methods
class Formatter:
    @singledispatchmethod
    def format(self, value):
        raise NotImplementedError
    
    @format.register
    def _(self, value: int) -> str:
        return f"int: {value}"
```

### `reduce`
```python
from functools import reduce
import operator

reduce(operator.add, [1, 2, 3, 4], 0)   # 10 (with initial)
reduce(operator.mul, [1, 2, 3, 4])      # 24 (no initial)
reduce(lambda acc, x: acc + [x*2], items, [])
```

- Left fold: `reduce(f, [a,b,c], init) = f(f(f(init, a), b), c)`
- Prefer explicit loops for readability in most cases

### `cmp_to_key`
```python
from functools import cmp_to_key

def compare(a, b):
    return (a > b) - (a < b)  # -1, 0, 1

sorted(items, key=cmp_to_key(compare))
```

- Convert old-style comparison function to key function
- Needed for complex sorting not expressible as key

### `total_ordering`
```python
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, major, minor, patch):
        self.tuple = (major, minor, patch)
    
    def __eq__(self, other):
        return self.tuple == other.tuple
    
    def __lt__(self, other):
        return self.tuple < other.tuple
# Generates __le__, __gt__, __ge__, __ne__
```

- Define `__eq__` + one of `__lt__`, `__le__`, `__gt__`, `__ge__`
- Generates the rest

---

## Decision Rules

| Need | Tool |
|------|------|
| Fix some arguments | `partial` / `partialmethod` |
| Cache pure function results | `lru_cache` / `cache` |
| Cache instance property | `cached_property` |
| Single-dispatch generic function | `singledispatch` |
| Single-dispatch method | `singledispatchmethod` |
| Reduce sequence to single value | `reduce` (or explicit loop) |
| Old-style comparison to key | `cmp_to_key` |
| Auto-generate comparisons | `total_ordering` |
| Preserve decorator metadata | `wraps` (ALWAYS) |

---

## Preferred Patterns

```python
# Configurable retry with partial
retry_3 = partial(retry, times=3, delay=1.0)
retry_5 = partial(retry, times=5, delay=0.5)

# Cached property for expensive computation
class Service:
    def __init__(self, config):
        self.config = config
    
    @cached_property
    def client(self) -> APIClient:
        return APIClient(self.config.api_key, timeout=self.config.timeout)

# Generic function for extensible serialization
@singledispatch
def to_json(obj) -> str:
    raise TypeError(f"Type {type(obj)} not serializable")

@to_json.register
def _(obj: datetime) -> str:
    return obj.isoformat()

@to_json.register
def _(obj: UUID) -> str:
    return str(obj)
```

---

## Avoid

- `lru_cache` on functions with side effects
- `lru_cache` on methods without `maxsize` (memory leak — instance never freed)
- `cached_property` with mutable return values (shared reference)
- `reduce` for simple aggregations (`sum`, `max`, `min`, `any`, `all`)
- `partial` with mutable default arguments
- Forgetting `@wraps` on decorators

---

## Validation Considerations

- `cache_info()` for cache effectiveness monitoring
- `typed=True` prevents `1` and `1.0` sharing cache entry
- Thread safety: `lru_cache` yes, `cached_property` no

---

## Related Skills

- `core/advanced_python.md` (decorators)
- `core/functions.md`
- `generation/async_concurrency.md` (async caching)
- `quality/functions.md`