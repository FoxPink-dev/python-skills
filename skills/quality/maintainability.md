---
name: maintainability
purpose: Avoid unnecessary coupling and complexity for long-term maintenance.
category: quality
triggers:
  - maintainability
  - complexity
  - coupling
  - cohesion
  - solid
dependencies: []
related: []
priority: supporting
estimated_tokens: 1000
---
# Quality: Maintainability

**Purpose**: Avoid unnecessary coupling and complexity for long-term maintenance.

**When to use**: Architecture decisions, refactoring, code review.
---
---
name: quality_maintainability
purpose: Avoid unnecessary coupling and complexity for long-term maintenance
category: quality
triggers:
  - coupling
  - cohesion
  - complexity
  - architecture
  - god class
  - circular dependency
dependencies:
  - quality/abstractions.md
  - quality/duplication.md
  - quality/functions.md
  - generation/protocols_generics.md
  - engineering/modules_packages.md
priority: primary
estimated_tokens: 1400
---

## Core Rules

### Coupling
- **Low coupling**: Modules interact through well-defined interfaces
- **High cohesion**: Related functionality grouped together

```python
# GOOD — low coupling via protocol
class PaymentProcessor(Protocol):
    def charge(self, amount: int, token: str) -> ChargeResult: ...

def process_order(order: Order, processor: PaymentProcessor) -> Result:
    ...

# BAD — high coupling to concrete implementation
def process_order(order: Order, processor: StripeProcessor) -> Result:
    ...
```

### Dependency Direction
```
Domain (business logic)     <--  DOES NOT DEPEND ON  -->  Infrastructure (DB, HTTP, UI)
       ^                                                         ^
       +-- Depends on abstractions --+
```

- Domain defines interfaces (Protocols)
- Infrastructure implements them
- Application wires them together

### Complexity Metrics
| Metric | Threshold | Action |
|--------|-----------|--------|
| Cyclomatic complexity | >10 | Refactor |
| Function length | >50 lines | Split |
| Class length | >300 lines | Split |
| Parameters | >7 | Use config object |
| Nesting depth | >3 | Extract/guard clauses |

### Single Responsibility
- Each module/class/function has one reason to change
- If you can't name it simply, it does too much

### Change Amplification
- A change in one place should not require changes in many others
- If adding a field requires changes in 5+ files, design is too coupled
- Use dependency inversion to contain changes

---

## Decision Rules

| Situation | Approach |
|-----------|----------|
| New feature | Add to existing cohesive module or create new |
| Shared code | Extract to utility only if used 3+ times |
| Cross-cutting concern | Decorator / middleware / context manager |
| Configuration | Central config object, not global constants |

---

## Preferred Patterns

```python
# Config object instead of many parameters
@dataclass
class ProcessingConfig:
    timeout: float = 30.0
    retries: int = 3
    validate: bool = True
    callback: Callable[[str], None] | None = None

def process(data: Data, config: ProcessingConfig) -> Result:
    ...

# Protocol for dependency inversion
class Cache(Protocol):
    async def get(self, key: str) -> bytes | None: ...
    async def set(self, key: str, value: bytes, ttl: int) -> None: ...

class Service:
    def __init__(self, cache: Cache):
        self.cache = cache  # Depends on abstraction
```

---

## Avoid

- God classes (knows everything, does everything)
- Circular dependencies between modules
- Global mutable state
- Hardcoded infrastructure in domain logic
- Premature abstraction (wait for 3rd use case)
- Copy-paste modification (refactor instead)

---

## Validation Considerations

- `radon cc` for cyclomatic complexity
- `xenon` for complexity thresholds
- Import graph analysis (no cycles)
- Architecture tests (import-linter, pydeps)
- `ruff` B007 (loop variable in closure)

---

## Related Skills

- `quality/abstractions.md`
- `quality/duplication.md`
- `quality/functions.md`
- `generation/protocols_generics.md`
- `engineering/modules_packages.md`