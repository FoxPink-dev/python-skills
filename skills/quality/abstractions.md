# Quality: Abstractions

**Purpose**: When and how to create abstractions.

**When to use**: Refactoring, designing new modules, avoiding duplication.

---

## Core Rules

### Abstraction Principles

1. **Wait for 3** — Don't abstract until 3+ concrete use cases
2. **Prefer composition** — Over inheritance
3. **Depend on abstractions** — Protocols/Interfaces, not concretions
4. **Leaky abstractions** — Avoid (abstraction reveals implementation details)
5. **Wrong abstraction** — Worse than duplication (prefer duplication over wrong abstraction)

### When to Abstract
```python
# GOOD — 3+ similar patterns
def process_user(user):
    validate(user)
    save(user)
    notify(user)

def process_order(order):
    validate(order)
    save(order)
    notify(order)

def process_payment(payment):
    validate(payment)
    save(payment)
    notify(payment)

# Abstract to:
def process_entity(entity: Entity):
    validate(entity)
    save(entity)
    notify(entity)
```

### When NOT to Abstract
```python
# BAD — premature, different semantics
def process_user(user):
    validate_email(user.email)
    save_user(user)
    send_welcome_email(user)

def process_file(file):
    validate_checksum(file.checksum)
    save_file(file)
    index_file(file)

# These are DIFFERENT operations, not same pattern
```

### Interface Design
```python
# GOOD — Protocol (structural, flexible)
class Repository(Protocol[T]):
    def get(self, id: str) -> T | None: ...
    def save(self, entity: T) -> T: ...

# GOOD — ABC (when runtime check needed)
class Cache(ABC):
    @abstractmethod
    def get(self, key: str) -> bytes | None: ...
    @abstractmethod
    def set(self, key: str, value: bytes, ttl: int) -> None: ...

# BAD — Concrete base class forcing inheritance
class BaseRepository:
    def get(self, id: str) -> User:
        return self.db.query(User).filter_by(id=id).first()
```

### Abstraction Levels
```
High-level policy (business rules)
       ↓
Application services (orchestration)
       ↓
Domain services (business logic)
       ↓
Infrastructure (DB, HTTP, FS)
```

- Each layer depends only on layer below
- Domain has NO dependencies on infrastructure

---

## Decision Rules

| Situation | Action |
|-----------|--------|
| 3+ similar implementations | Abstract |
| 1-2 implementations | Keep concrete |
| Different semantics | Don't abstract |
| Need runtime swap | Protocol/ABC |
| Compile-time only | Protocol |
| Cross-cutting (logging, timing) | Decorator/middleware |

---

## Preferred Patterns

```python
# Strategy pattern via Protocol
class Exporter(Protocol):
    def export(self, data: Data) -> bytes: ...

class JSONExporter:
    def export(self, data: Data) -> bytes:
        return json.dumps(data).encode()

class CSVExporter:
    def export(self, data: Data) -> bytes:
        return csv_encode(data)

def export_data(data: Data, exporter: Exporter) -> bytes:
    return exporter.export(data)
```

---

## Avoid

- Abstract base classes with concrete methods (use composition)
- Deep inheritance hierarchies (>2 levels)
- "Manager", "Handler", "Utils", "Helper" classes
- Abstracting control flow (use functions)
- Frameworks (inverting control) vs libraries (you call them)

---

## Validation Considerations

- Can implementations be swapped without changing consumers?
- Are protocols minimal (only what's needed)?
- Does abstraction leak implementation details?
- Is there a test for each implementation?

---

## Related Skills

- `quality/maintainability.md`
- `quality/duplication.md`
- `generation/protocols_generics.md`
- `core/oop.md`