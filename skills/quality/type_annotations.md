---
name: type_annotations
purpose: Appropriate type hints — useful, not noise.
category: quality
triggers:
  - type-annotation
  - hint
  - mypy
  - pyright
  - optional
  - union
dependencies: []
related: []
priority: supporting
estimated_tokens: 1007
---
# Quality: Type Annotations

**Purpose**: Appropriate type hints — useful, not noise.

**When to use**: All code generation. Quality type hints improve maintainability.

---

## Core Rules

### When to Annotate
| Element | Annotate? |
|---------|-----------|
| Public function signature | Yes |
| Public method signature | Yes |
| Class attributes | Yes |
| Module-level constants | Yes |
| Local variables | Usually no (inference) |
| Loop variables | No |
| Trivial helpers | Optional |

### Useful vs Noise

```python
# USEFUL — public API, complex types
def fetch_users(
    client: APIClient,
    filters: UserFilters | None = None,
    limit: int = 100,
) -> list[User]:
    ...

# USEFUL — generic class
class Repository(Generic[T]):
    def get(self, id: str) -> T | None: ...

# NOISE — obvious inference
count: int = 0
name: str = "default"
items: list[str] = []
for i, item in enumerate(items):  # i inferred as int
    ...

# NOISE — over-specified
def add(a: int, b: int) -> int:
    return a + b
```

### Type Hint Style
```python
# Python 3.9+ — prefer built-in generics
list[str]
dict[str, int]
set[int]
tuple[int, str]
tuple[int, ...]  # variable length

# Union — Python 3.10+
int | str
list[int | str]

# Optional
str | None

# Callable
Callable[[int, str], bool]
# Or collections.abc.Callable

# Type alias (3.12+)
type UserID = int
type JSONValue = str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]
```

### Strictness Levels
```toml
# pyproject.toml — mypy config
[tool.mypy]
# Strict (recommended for new projects)
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true

# Gradual adoption — per module
[[tool.mypy.overrides]]
module = "legacy.*"
disallow_untyped_defs = false
```

### TypedDict for External Data
```python
from typing import TypedDict, NotRequired

class UserAPIResponse(TypedDict):
    id: int
    name: str
    email: str
    created_at: str  # ISO format
    metadata: NotRequired[dict[str, str]]  # Optional key

def parse_user(data: UserAPIResponse) -> User:
    return User(
        id=data["id"],
        name=data["name"],
        email=data["email"],
        created_at=datetime.fromisoformat(data["created_at"]),
    )
```

### Protocol for Interfaces
```python
from typing import Protocol

class Cache(Protocol):
    def get(self, key: str) -> bytes | None: ...
    def set(self, key: str, value: bytes, ttl: int) -> None: ...

# Any object with get/set implements Cache (no inheritance needed)
```

---

## Decision Rules

| Situation | Annotation Level |
|-----------|------------------|
| New project | Strict (`mypy --strict`) |
| Existing project | Match project config |
| Public library | Full annotations + `py.typed` |
| Internal app | Public API annotated, internal inferred |
| Prototyping | Minimal |

---

## Preferred Patterns

```python
# Function with full hints
def process_order(
    order: Order,
    inventory: InventoryService,
    payment: PaymentGateway,
    *,
    idempotency_key: str | None = None,
) -> OrderResult:
    ...

# Class with typed attributes
class Config:
    database_url: str
    pool_size: int = 10
    timeout: float = 30.0
    debug: bool = False

# Generic with constraints
T = TypeVar("T", bound=Entity)

class Repository(Generic[T]):
    def get(self, id: str) -> T | None: ...
    def list(self) -> list[T]: ...
```

---

## Avoid

- `Any` without `# type: ignore[...]` justification
- `object` as "unknown type" (use `Any` or proper protocol)
- Overly complex nested types without aliases
- Type hints that are wrong (lying types)
- Ignoring mypy errors without comment

---

## Validation Considerations

- `mypy --strict` passes
- `pyright` passes
- No `# type: ignore` without error code
- `py.typed` marker for libraries

---

## Related Skills

- `generation/type_hints.md`
- `generation/protocols_generics.md`
- `engineering/pyproject_toml.md`
- `quality/readability.md`