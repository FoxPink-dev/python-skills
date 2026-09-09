# Generation: Protocols and Generics

**Purpose**: Advanced typing with protocols, generics, and variance.

**When to use**: Designing flexible, decoupled interfaces and reusable components.

---

## Core Rules

### Protocols (Structural Subtyping)
```python
from typing import Protocol, runtime_checkable

# Basic protocol
class Serializable(Protocol):
    def to_json(self) -> str: ...
    def to_bytes(self) -> bytes: ...

# With generics
T = TypeVar("T")

class Repository(Protocol[T]):
    def get(self, id: str) -> T: ...
    def save(self, entity: T) -> None: ...
    def delete(self, id: str) -> bool: ...

# Runtime checkable (for isinstance)
@runtime_checkable
class Configurable(Protocol):
    def configure(self, settings: dict) -> None: ...

# Multiple protocols
class Service(Repository[User], Configurable, Protocol):
    def start(self) -> None: ...
```

### Protocol vs ABC
| Feature | Protocol | ABC |
|---------|----------|-----|
| Inheritance required | No | Yes |
| Runtime isinstance | Only `@runtime_checkable` | Yes |
| Multiple implementations | Easy | Requires inheritance |
| Third-party classes | Works if structure matches | Must subclass |
| Method enforcement | Static only | Static + runtime |

**Prefer Protocol** for interfaces unless runtime checks needed.

### Generic Classes
```python
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value
    
    def get(self) -> T:
        return self._value
    
    def map[U](self, func: Callable[[T], U]) -> Box[U]:
        return Box(func(self._value))

# Multiple type vars
class Pair(Generic[T, U]):
    def __init__(self, first: T, second: U) -> None:
        self.first = first
        self.second = second
```

### Variance (Covariance/Contravariance)
```python
from typing import TypeVar, Generic, Protocol

# Covariant (output only) — use +T
T_co = TypeVar("T_co", covariant=True)

class Producer(Generic[T_co]):
    def produce(self) -> T_co: ...

# Contravariant (input only) — use -T
T_contra = TypeVar("T_contra", contravariant=True)

class Consumer(Generic[T_contra]):
    def consume(self, item: T_contra) -> None: ...

# Invariant (both) — default
T = TypeVar("T")

class Processor(Generic[T]):
    def process(self, item: T) -> T: ...
```

### Variance Rules
| Position | Variance |
|----------|----------|
| Return type | Covariant (+) |
| Argument type | Contravariant (-) |
| Mutable attribute | Invariant |
| Read-only property | Covariant |

### Protocol Variance
```python
T_co = TypeVar("T_co", covariant=True)

class Readable(Protocol[T_co]):
    def read(self) -> T_co: ...  # Covariant OK

T_contra = TypeVar("T_contra", contravariant=True)

class Writable(Protocol[T_contra]):
    def write(self, data: T_contra) -> None: ...  # Contravariant OK
```

### Constrained TypeVars
```python
# Only these types allowed
T = TypeVar("T", int, float, str)

def process(x: T) -> T:  # Only int, float, str accepted
    return x
```

### Bound TypeVars
```python
# Must be subclass of bound
T = TypeVar("T", bound="BaseEntity")

class BaseEntity:
    id: int

def save(entity: T) -> T:  # Must be BaseEntity subclass
    return entity
```

### Higher-Kinded Types (Simulated)
```python
from typing import TypeVar, Generic, Callable

# Functor-like
F = TypeVar("F", bound=Callable[..., Any])

def map_func[F](func: Callable[[A], B], fa: F[A]) -> F[B]:  # Not directly expressible
    ...

# Use protocols for typeclass-like patterns
class Functor(Protocol[T]):
    def map[U](self, func: Callable[[T], U]) -> "Functor[U]": ...
```

### Type Parameters (Python 3.12+)
```python
# New syntax
class Box[T]:
    def __init__(self, value: T) -> None:
        self.value = value
    
    def get(self) -> T:
        return self.value

def identity[T](x: T) -> T:
    return x
```

---

## Decision Rules

| Need | Pattern |
|------|---------|
| Interface for duck typing | `Protocol` |
| Interface needing `isinstance` | `@runtime_checkable Protocol` |
| Reusable container | `Generic[T]` |
| Read-only collection | `Generic[+T]` (covariant) |
| Callback handler | `Generic[-T]` (contravariant) |
| Limited type set | `TypeVar("T", A, B, C)` |
| Subtype constraint | `TypeVar("T", bound=Base)` |
| Self-returning methods | `Self` (3.11+) |

---

## Preferred Patterns

```python
# Repository pattern with protocol
class UserRepo(Protocol):
    def get(self, id: UserID) -> User | None: ...
    def list(self, filter: UserFilter) -> list[User]: ...
    def save(self, user: User) -> User: ...

# Generic service
class CrudService(Generic[T]):
    def __init__(self, repo: Repository[T]) -> None:
        self.repo = repo
    
    def get_or_create(self, id: str, factory: Callable[[], T]) -> T:
        if (existing := self.repo.get(id)) is not None:
            return existing
        new = factory()
        self.repo.save(new)
        return new

# Covariant read-only view
class ReadOnlyList(Generic[T_co]):
    def __init__(self, items: list[T_co]) -> None:
        self._items = tuple(items)
    
    def __getitem__(self, i: int) -> T_co:
        return self._items[i]
    
    def __iter__(self) -> Iterator[T_co]:
        return iter(self._items)
```

---

## Avoid

- Overusing generics (YAGNI)
- Invariant generics when covariant/contravariant works
- `@runtime_checkable` on large protocols (performance)
- Complex variance without clear need
- Protocols with too many methods (split them)

---

## Validation Considerations

- `mypy --strict` catches variance errors
- Protocol conformance checked structurally
- `isinstance(obj, Protocol)` only works with `@runtime_checkable`

---

## Related Skills

- `generation/type_hints.md`
- `core/oop.md` (ABCs)
- `quality/abstractions.md`
- `engineering/dependency_management.md`