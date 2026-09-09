# Generation: Type Hints

**Purpose**: Modern Python typing guidance for code generation.

**When to use**: All code generation. Type hints improve correctness and maintainability.

---

## Core Rules

### Basic Annotations
```python
# Variables
count: int = 0
name: str = "default"
items: list[str] = []
mapping: dict[str, int] = {}

# Functions
def func(arg: int, optional: str = "default") -> bool:
    ...

# Classes
class MyClass:
    attr: int
    def method(self, x: float) -> str: ...
```

### Built-in Generics (Python 3.9+)
```python
# Preferred (no typing import needed)
list[str]
dict[str, int]
set[int]
tuple[int, str, bool]
tuple[int, ...]      # Variable-length tuple
collections.abc.Iterable[int]
collections.abc.Sequence[str]
collections.abc.Mapping[str, int]
```

### Union Types (Python 3.10+)
```python
# Preferred
int | str
list[int | str]
dict[str, int | None]

# Legacy (still works)
from typing import Union
Union[int, str]
```

### Optional
```python
# Python 3.10+
str | None

# Legacy
from typing import Optional
Optional[str]
```

### Type Aliases (Python 3.12+)
```python
type JSONValue = str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]
type UserID = int
```

### TypeVar and Generics
```python
from typing import TypeVar, Generic

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
    
    def get(self) -> T:
        return self.value

# Usage
int_container: Container[int] = Container(42)
```

### Protocols (Structural Typing)
```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:  # Implicitly implements Drawable
        ...

def render(d: Drawable) -> None:
    d.draw()
```

### Callable Types
```python
from typing import Callable

# Function taking (int, str) returning bool
callback: Callable[[int, str], bool]

# More flexible
from collections.abc import Callable
handler: Callable[..., Any]
```

### TypedDict (Structured Dicts)
```python
from typing import TypedDict, NotRequired

class UserDict(TypedDict):
    id: int
    name: str
    email: NotRequired[str]  # Optional key (3.11+)
    # or: email: str | None  # Required key, nullable value

def process_user(user: UserDict) -> None:
    print(user["name"])
```

### Dataclasses with Types
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: Optional[str] = None
    tags: list[str] = field(default_factory=list)
```

### Overloads
```python
from typing import overload

@overload
def func(x: int) -> int: ...
@overload
def func(x: str) -> str: ...
def func(x: int | str) -> int | str:
    return x
```

### Final and Literal
```python
from typing import Final, Literal

MAX_SIZE: Final = 100
Mode = Literal["fast", "slow", "auto"]
mode: Mode = "fast"
```

### Self Type (Python 3.11+)
```python
from typing import Self

class Builder:
    def set_name(self, name: str) -> Self:
        self.name = name
        return self
    
    def build(self) -> Product:
        return Product(self.name)
```

### Type Narrowing
```python
def process(value: int | str) -> str:
    if isinstance(value, int):
        return str(value)  # value is int here
    return value           # value is str here

# With user-defined guards
from typing import TypeGuard

def is_int_list(value: list[int] | list[str]) -> TypeGuard[list[int]]:
    return all(isinstance(x, int) for x in value)

if is_int_list(items):
    # items is list[int] here
    ...
```

---

## Decision Rules

| Situation | Choice |
|-----------|--------|
| Simple function | Full annotations |
| Internal helper | Light annotations or inference |
| Public API | Full annotations + docstring |
| Generic container | `Generic[T]` |
| Interface | `Protocol` |
| Dict with fixed keys | `TypedDict` |
| Union of few types | `A | B` |
| Many union types | `Union[A, B, C, ...]` |
| Callable | `Callable[[Args], Return]` |
| Constant | `Final` |
| Limited string values | `Literal` |

---

## Useful vs Noise

### Useful
- Function signatures (public API)
- Complex data structures
- Generic classes
- Protocol interfaces
- Return types of non-trivial functions

### Noise
- Obvious local variables: `x: int = 5`
- Loop variables: `for i: int in range(10):`
- Trivial helpers with clear types
- Over-annotating private implementation

---

## Project Compatibility

Respect project's Python version and config:
- Check `pyproject.toml` for `[tool.mypy]` or `[tool.pyright]`
- Python 3.9+: built-in generics
- Python 3.10+: `|` union, `TypeGuard`
- Python 3.11+: `Self`, `NotRequired`, `TypedDict` improvements
- Python 3.12+: `type` alias, `**kwargs` typing

---

## Preferred Patterns

```python
# Public API — full types
def fetch_users(
    client: APIClient,
    filters: UserFilters | None = None,
    limit: int = 100,
) -> list[User]:
    ...

# Internal — inference OK
def _parse_line(line: str) -> ParsedLine:
    parts = line.split(",")
    return ParsedLine(int(parts[0]), parts[1])

# Generic utility
def first_item[T](items: Sequence[T]) -> T | None:
    return items[0] if items else None
```

---

## Avoid

- `Any` without justification (disable checking)
- `object` as "I don't know" (use `Any` or proper type)
- Complex nested types without aliases
- Type hints that lie (incorrect types)
- Ignoring type checker errors without `# type: ignore` comment with reason

---

## Validation Considerations

- Run type checker (`mypy`, `pyright`) on project
- `--strict` mode for new projects
- `# type: ignore[code]` with specific error code
- `typing.TYPE_CHECKING` for imports only needed for types

---

## Related Skills

- `generation/protocols_generics.md`
- `generation/workflow.md`
- `quality/type_annotations.md`
- `engineering/pyproject_toml.md` (tool config)