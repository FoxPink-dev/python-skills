# Core: Variables and Types

**Purpose**: Fundamental Python variable and type knowledge for code generation.

**When to use**: Always active. Foundation for all Python code generation.

---

## Core Rules

### Variable Assignment
- Variables are references to objects
- Assignment binds a name to an object
- Multiple assignment: `a = b = 1` (same object), `a, b = 1, 2` (tuple unpacking)
- No declaration needed — assignment creates the variable

### Primitive Types
| Type | Literal | Immutable | Use For |
|------|---------|-----------|---------|
| `int` | `42`, `0b101`, `0x2A` | Yes | Whole numbers, arbitrary precision |
| `float` | `3.14`, `1e-5` | Yes | Decimal numbers (IEEE 754) |
| `bool` | `True`, `False` | Yes | Logic (subclass of `int`) |
| `str` | `"text"`, `'text'`, `"""multiline"""` | Yes | Text (Unicode) |
| `bytes` | `b"data"` | Yes | Binary data |
| `None` | `None` | Yes | Absence of value |

### Type Identity vs Equality
- `is` — identity (same object in memory)
- `==` — equality (value comparison)
- Use `is` only for `None`, `True`, `False`, sentinel objects
- Never use `is` for strings, numbers, or custom objects

### Mutable vs Immutable
**Immutable**: `int`, `float`, `bool`, `str`, `bytes`, `tuple`, `frozenset`, `None`
**Mutable**: `list`, `dict`, `set`, `bytearray`, custom objects

**Critical**: Mutable objects as default arguments create shared state (see anti-patterns)

### Type Inspection
```python
type(obj)           # Exact type
isinstance(obj, T)  # Type check (supports unions, inheritance)
hasattr(obj, attr)  # Attribute existence
```

---

## Decision Rules

| Situation | Choice |
|-----------|--------|
| Need arbitrary precision integer | `int` (native) |
| Need exact decimal arithmetic | `decimal.Decimal` |
| Need fraction arithmetic | `fractions.Fraction` |
| Text data | `str` |
| Binary data / protocols | `bytes` |
| Fixed collection of heterogeneous items | `tuple` or `NamedTuple` / `dataclass` |
| Ordered, mutable collection | `list` |
| Key-value mapping | `dict` |
| Unique items, membership testing | `set` |
| Immutable unique items | `frozenset` |

---

## Preferred Patterns

```python
# Type annotation for clarity (optional but recommended)
count: int = 0
name: str = "default"
items: list[str] = []
mapping: dict[str, int] = {}

# Sentinel for "not provided" (not None)
_SENTINEL = object()

def func(arg=_SENTINEL):
    if arg is _SENTINEL:
        arg = compute_default()
```

---

## Avoid

- Using `is` for string/number comparison
- Treating mutable objects as immutable
- Assuming `bool` is only `True`/`False` (it's subclass of `int`)
- Type inspection via `type(obj) == SomeClass` (use `isinstance`)
- Chained assignment for mutable objects: `a = b = []` (both reference same list)

---

## Validation Considerations

- Type checkers catch many primitive type errors
- Runtime `isinstance` checks for external input
- `mypy --strict` catches implicit `Any`

---

## Related Skills

- `core/data_structures.md`
- `core/functions.md` (mutable defaults)
- `generation/type_hints.md`
- `anti_patterns/index.md` (mutable defaults)