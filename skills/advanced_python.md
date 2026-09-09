# Core: Advanced Python

**Purpose**: Iterators, generators, decorators, context managers, descriptors.

**When to use**: Implementing advanced patterns, libraries, or frameworks.

---

## Core Rules

### Iterators
```python
class Iterator:
    def __iter__(self) -> Iterator:
        return self
    
    def __next__(self) -> Item:
        if done:
            raise StopIteration
        return next_item

# Usage
for item in Iterator():
    ...
```

- Implement `__iter__` (returns self) and `__next__`
- Raise `StopIteration` when exhausted
- Prefer generators for simple iterators

### Generators
```python
def generator() -> Generator[Item, None, None]:
    for i in range(10):
        yield i
        yield from other_generator()  # Delegate

# Generator expression
gen = (x * 2 for x in range(10))
```

- `yield` produces value, suspends function
- `yield from` delegates to sub-generator
- Lazy evaluation — computes on demand
- Can receive values via `send()` (rare)

### Decorators
```python
import functools

def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pre()
        try:
            return func(*args, **kwargs)
        finally:
            post()
    return wrapper

# With arguments
def decorator_with_args(arg):
    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return actual_decorator

@decorator_with_args("value")
def func():
    ...
```

- **Always** use `@functools.wraps(func)` on wrapper
- Decorators execute at **definition time**
- Class decorators receive class, return class

### Context Managers
```python
# Class-based
class Resource:
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False  # Don't suppress exceptions

# Generator-based (contextlib)
from contextlib import contextmanager

@contextmanager
def resource():
    r = acquire()
    try:
        yield r
    finally:
        r.release()

# Usage
with resource() as r:
    r.use()
```

- `__exit__` receives exception info; return `True` to suppress
- `@contextmanager` yields once; cleanup in `finally`
- Use for resource management (files, locks, connections, transactions)

### Descriptors
```python
class Descriptor:
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj._value
    
    def __set__(self, obj, value):
        obj._value = value
    
    def __delete__(self, obj):
        del obj._value

class MyClass:
    attr = Descriptor()
```

- Protocol: `__get__`, `__set__`, `__delete__`
- Data descriptors (`__set__` or `__delete__`) override instance `__dict__`
- Non-data descriptors (only `__get__`) overridden by instance `__dict__`
- Used by: `property`, `classmethod`, `staticmethod`, `field`

### Metaclasses (Rare)
```python
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        # Modify class creation
        return super().__new__(mcs, name, bases, namespace)

class MyClass(metaclass=Meta):
    ...
```

- Customize class creation
- Use sparingly; prefer `__init_subclass__` (Python 3.6+)

### `__init_subclass__`
```python
class Base:
    subclasses = []
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Base.subclasses.append(cls)
```

- Called when subclass is defined
- Simpler than metaclasses for registration

---

## Decision Rules

| Need | Tool |
|------|------|
| Simple iteration | Generator function |
| Complex iterator state | Iterator class |
| Resource cleanup | Context manager (`@contextmanager` or class) |
| Cross-cutting behavior | Decorator |
| Attribute access control | Descriptor / `property` |
| Class registration | `__init_subclass__` |
| Class creation control | Metaclass (last resort) |

---

## Preferred Patterns

```python
# Generator for lazy sequences
def read_lines(path: Path) -> Generator[str, None, None]:
    with path.open() as f:
        for line in f:
            yield line.rstrip('\n')

# Context manager for temp resources
@contextmanager
def temp_dir():
    path = Path(tempfile.mkdtemp())
    try:
        yield path
    finally:
        shutil.rmtree(path)

# Decorator with args preserving signature
def retry(times: int = 3, delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == times - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator
```

---

## Avoid

- Generators that don't clean up resources (use `try/finally` or context manager)
- Decorators without `@functools.wraps`
- Complex metaclasses when `__init_subclass__` suffices
- Descriptors for simple attribute access (use `@property`)
- `yield` in `finally` block (confusing semantics)
- Mixing `yield` and `return` with values in same generator

---

## Validation Considerations

- `contextlib.closing` for objects with `close()`
- `contextlib.AsyncExitStack` for async context managers
- Type checkers understand generator types: `Generator[Yield, Send, Return]`
- `inspect.isgeneratorfunction()`, `inspect.isgenerator()`

---

## Related Skills

- `generation/async_concurrency.md` (async generators, context managers)
- `generation/error_handling.md` (context manager exception handling)
- `stdlib/functools.md` (wraps, lru_cache)
- `quality/functions.md`
- `anti_patterns/index.md`