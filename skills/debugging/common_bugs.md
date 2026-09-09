# Debugging: Common Bugs

**Purpose**: Quick reference for frequent Python bug patterns.

**When to use**: Debugging, code review, preventing known issues.

---

## Core Rules

### Mutable Default Arguments
```python
# BUG
def append_item(item, items=[]):
    items.append(item)
    return items

append_item(1)  # [1]
append_item(2)  # [1, 2] — BUG: shared list!

# FIX
def append_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### Late Binding in Closures
```python
# BUG
funcs = []
for i in range(3):
    funcs.append(lambda: i)
    
[f() for f in funcs]  # [2, 2, 2] — all capture same i!

# FIX — bind early
funcs = []
for i in range(3):
    funcs.append(lambda i=i: i)  # Default binds current value
    
# OR use functools.partial
from functools import partial
funcs = [partial(lambda x: x, i) for i in range(3)]
```

### Integer Division (Python 2 vs 3)
```python
# Python 3: / is float division, // is integer
3 / 2   # 1.5
3 // 2  # 1

# In Python 2: / was integer division for ints
# Not an issue in Python 3+
```

### Floating Point Precision
```python
# BUG
0.1 + 0.2 == 0.3  # False! 0.30000000000000004

# FIX — use Decimal for money/precision
from decimal import Decimal
Decimal("0.1") + Decimal("0.2") == Decimal("0.3")  # True

# Or use tolerance
abs(0.1 + 0.2 - 0.3) < 1e-9  # True
```

### Variable Shadowing
```python
# BUG
def process(items):
    list = []  # Shadows built-in list!
    for item in items:
        list.append(transform(item))
    return list

# FIX — never shadow builtins
def process(items):
    result = []
    for item in items:
        result.append(transform(item))
    return result
```

### Iterable Exhaustion
```python
# BUG
gen = (x for x in range(3))
list(gen)  # [0, 1, 2]
list(gen)  # [] — exhausted!

# FIX — convert to list if reused
gen = list(x for x in range(3))
list(gen)  # [0, 1, 2]
list(gen)  # [0, 1, 2]
```

### Default Dict Mutation
```python
# BUG
from collections import defaultdict

def add_item(key, value, d=defaultdict(list)):
    d[key].append(value)
    return d

add_item("a", 1)  # {"a": [1]}
add_item("b", 2)  # {"a": [1], "b": [2]} — SHARED!

# FIX
def add_item(key, value, d=None):
    if d is None:
        d = defaultdict(list)
    d[key].append(value)
    return d
```

### Exception Swallowing
```python
# BUG
try:
    risky()
except:
    pass  # Swallows everything including KeyboardInterrupt!

# FIX — specific exceptions
try:
    risky()
except SpecificError:
    handle()
except Exception:
    logger.exception("Unexpected error")
    raise
```

### Modifying During Iteration
```python
# BUG
items = [1, 2, 3, 4, 5]
for item in items:
    if item % 2 == 0:
        items.remove(item)  # Skips elements!

# FIX — iterate over copy
for item in items[:]:  # or list(items)
    if item % 2 == 0:
        items.remove(item)

# OR filter
items = [x for x in items if x % 2 != 0]
```

### String/Bytes Confusion
```python
# BUG
data = b"hello"
data + " world"  # TypeError: can't concat bytes to str

# FIX — explicit encode/decode
data.decode() + " world"  # "hello world"
data + b" world"          # b"hello world"
```

### Path Traversal (Security)
```python
# BUG
def read_file(filename):
    with open(filename) as f:  # User controls path!
        return f.read()

# FIX — validate path
def read_file(filename, base_dir):
    path = (Path(base_dir) / filename).resolve()
    if not path.is_relative_to(base_dir):
        raise SecurityError("Path traversal")
    return path.read_text()
```

---

## Decision Rules

| Symptom | Likely Cause |
|---------|--------------|
| State persists across calls | Mutable default argument |
| Loop variable wrong in closure | Late binding |
| Money calculations wrong | Float precision |
| First/last element wrong | Off-by-one |
| Intermittent failures | Race condition / shared state |
| Unicode errors | Bytes/str confusion |
| Second iteration empty | Iterator exhaustion |

---

## Avoid

- `except:` without exception type
- `list`, `dict`, `str` as variable names
- `float` for money
- Implicit iterator reuse
- User input in file paths without validation

---

## Validation Considerations

- `ruff` catches most of these (B006, B007, B008, etc.)
- `mypy` catches type issues
- Unit tests for edge cases
- Property-based testing finds edge cases

---

## Related Skills

- `debugging/root_cause.md`
- `anti_patterns/index.md`
- `security/input_validation.md`
- `generation/type_hints.md`