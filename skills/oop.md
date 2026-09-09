# Core: Object-Oriented Programming

**Purpose**: Python OOP patterns, inheritance, composition, and protocols.

**When to use**: Designing classes, inheritance hierarchies, or interfaces.

---

## Core Rules

### Class Definition
```python
class ClassName(BaseClass, AnotherBase):
    """Class docstring."""
    
    class_attr: ClassVar[int] = 0  # Class variable (type hint)
    
    def __init__(self, param: type) -> None:
        self.instance_attr: type = param
    
    def method(self) -> return_type:
        return self.instance_attr
    
    @classmethod
    def class_method(cls, arg: type) -> return_type:
        ...
    
    @staticmethod
    def static_method(arg: type) -> return_type:
        ...
    
    @property
    def computed(self) -> type:
        return derive(self.instance_attr)
```

### Inheritance
```python
class Base:
    def method(self) -> int:
        return 1

class Derived(Base):
    def method(self) -> int:
        return super().method() + 1  # Cooperative inheritance
```

- Use `super()` for cooperative multiple inheritance
- Method Resolution Order (MRO): C3 linearization (`Class.__mro__`)
- Prefer composition over inheritance for code reuse

### Abstract Base Classes (ABC)
```python
from abc import ABC, abstractmethod

class Interface(ABC):
    @abstractmethod
    def required(self) -> int:
        ...
    
    @property
    @abstractmethod
    def value(self) -> str:
        ...
    
    def concrete(self) -> str:
        return f"value: {self.value}"
```

### Protocols (Structural Subtyping, Python 3.8+)
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:  # Implicitly implements Drawable
        ...

def render(d: Drawable) -> None:
    d.draw()  # Accepts any object with draw()
```
- No explicit inheritance required
- Preferred over ABC for duck-typing interfaces
- `@runtime_checkable` for `isinstance` checks

### Dataclasses (Python 3.7+)
```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass(order=True, frozen=False)
class Point:
    x: float
    y: float
    label: str = ""              # Default
    metadata: dict = field(default_factory=dict)  # Mutable default
    _private: float = field(init=False, repr=False)  # Computed
    
    def __post_init__(self):
        self._private = self.x * self.y
```

### Magic Methods (Key Ones)
| Method | Purpose |
|--------|---------|
| `__init__` | Initialization |
| `__new__` | Instance creation (rare) |
| `__repr__` | Unambiguous representation (for debugging) |
| `__str__` | Readable representation (for users) |
| `__eq__`, `__hash__` | Equality and hashing (together!) |
| `__lt__`, `__le__`, `__gt__`, `__ge__` | Ordering |
| `__bool__` | Truth value |
| `__len__` | Length |
| `__getitem__`, `__setitem__`, `__delitem__` | Subscripting |
| `__iter__` | Iteration |
| `__contains__` | `in` operator |
| `__enter__`, `__exit__` | Context manager |
| `__call__` | Callable instances |
| `__getattr__`, `__getattribute__` | Attribute access |
| `__slots__` | Memory optimization, restrict attributes |

### Slots
```python
class Slotted:
    __slots__ = ('x', 'y')  # No __dict__, fixed attributes
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
```
- Reduces memory, prevents arbitrary attributes
- Incompatible with multiple inheritance (unless all parents use slots)

---

## Composition over Inheritance

```python
# Composition: has-a relationship
class Engine:
    def start(self) -> None: ...

class Car:
    def __init__(self, engine: Engine):
        self.engine = engine  # Delegation
    
    def start(self) -> None:
        self.engine.start()
```

- More flexible, testable, maintainable
- Avoid deep inheritance hierarchies (>2 levels)

---

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| Deep inheritance chains | Fragile, hard to maintain | Use composition |
| Multiple inheritance without clear design | Diamond problem | Use mixins or composition |
| `__del__` for cleanup | Unreliable, may not run | Use context managers |
| Properties with side effects | Surprising behavior | Keep properties pure |
| `type()` for type checks | Fragile, no subclass support | Use `isinstance()` |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Deep inheritance | Fragile, hard to maintain | Use composition |
| Mutable class attributes | Shared state across instances | Use instance attributes |
| Missing `super().__init__()` | Parent not initialized | Always call `super()` |
| `__eq__` without `__hash__` | Unhashable instances | Define both or use `frozen=True` |
| Properties with side effects | Surprising behavior | Keep properties pure |

### Anti-Pattern

```python
# NEVER: Deep inheritance
class A:
    def method(self): ...
class B(A):
    def method(self): ...
class C(B):
    def method(self): ...
class D(C):  # 4 levels deep!
    def method(self): ...

# NEVER: Mutable class attribute
class User:
    roles = []  # Shared across ALL instances!
    
# BETTER: Composition
class User:
    def __init__(self):
        self.roles = []  # Instance attribute
```

| Situation | Pattern |
|-----------|---------|
| Fixed schema, data container | `@dataclass` |
| Interface definition | `Protocol` (or `ABC` for runtime checks) |
| Shared behavior, single hierarchy | Inheritance |
| Reuse without hierarchy | Composition / Mixins |
| Value object (immutable) | `@dataclass(frozen=True)` |
| Need ordering | `@dataclass(order=True)` or `__lt__` |
| Need hashing in sets/dicts | `__eq__` + `__hash__` (or `frozen=True`) |
| Memory-critical many instances | `__slots__` |
| Dynamic attributes | Regular class (no slots) |

---

## Preferred Patterns

```python
# Immutable data carrier
@dataclass(frozen=True, slots=True)
class Config:
    host: str
    port: int
    timeout: float = 5.0

# Protocol for dependency inversion
class Repository(Protocol):
    def get(self, id: str) -> User: ...
    def save(self, user: User) -> None: ...

# Mixin for reusable behavior
class TimestampMixin:
    created_at: datetime
    updated_at: datetime
    
    def touch(self) -> None:
        self.updated_at = datetime.now()
```

---

## Avoid

- Deep inheritance chains (>2 levels)
- Multiple inheritance without clear design (diamond problem)
- Mutable class attributes shared across instances
- `__del__` (unreliable, use context managers)
- Overriding `__init__` without calling `super().__init__()`
- Using `type()` for type checks (use `isinstance`)
- Properties with side effects
- Getter/setter methods (use `@property`)

---

## Validation Considerations

- `mypy` verifies protocol conformance
- `@dataclass` generates `__init__`, `__repr__`, `__eq__`
- `slots=True` (Python 3.10+) enables slots on dataclasses
- `frozen=True` makes instances hashable (if all fields hashable)

---

## Related Skills

- `generation/protocols_generics.md`
- `generation/type_hints.md`
- `core/advanced_python.md` (descriptors, metaclasses)
- `quality/abstractions.md`
- `anti_patterns/index.md` (excessive inheritance)