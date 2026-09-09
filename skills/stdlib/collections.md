# Stdlib: collections

**Purpose**: Specialized container datatypes beyond built-ins.

**When to use**: When built-in list/dict/set don't fit the problem.

---

## Core Rules

### `namedtuple` / `NamedTuple`
```python
# Classic
from collections import namedtuple
Point = namedtuple("Point", ["x", "y"])

# Modern (Python 3.6+) — preferred
from typing import NamedTuple
class Point(NamedTuple):
    x: float
    y: float

# Usage
p = Point(1.0, 2.0)
p.x, p[0]  # Both work
```

- Immutable, hashable, lightweight
- NamedTuple supports type hints, methods, defaults

### `dataclass` vs `NamedTuple`
| Feature | `NamedTuple` | `@dataclass` |
|---------|--------------|--------------|
| Mutability | Immutable | Mutable (or `frozen=True`) |
| Methods | Yes | Yes |
| Defaults | Yes | Yes |
| Inheritance | Limited | Full |
| Performance | Slightly faster | Flexible |

### `defaultdict`
```python
from collections import defaultdict

# Auto-create missing keys
grouped = defaultdict(list)
for item in items:
    grouped[key(item)].append(item)

# Counter pattern
counts = defaultdict(int)
for item in items:
    counts[item] += 1

# Custom factory
def default_factory():
    return {"count": 0, "items": []}
```

### `Counter`
```python
from collections import Counter

c = Counter(["a", "b", "a", "c", "b", "a"])
# Counter({'a': 3, 'b': 2, 'c': 1})

c.most_common(2)        # [('a', 3), ('b', 2)]
c.total()               # 6 (Python 3.10+)
c.elements()            # Iterator over elements
c.update(["a", "d"])    # Add counts
c.subtract({"a": 1})    # Subtract counts

# Arithmetic
c1 + c2   # Add (keep positive)
c1 - c2   # Subtract (keep positive)
c1 & c2   # Intersection (min)
c1 | c2   # Union (max)
```

### `deque` (Double-Ended Queue)
```python
from collections import deque

d = deque([1, 2, 3], maxlen=5)  # Bounded (auto-discards old)

d.append(4)       # Right
d.appendleft(0)   # Left
d.pop()           # Right
d.popleft()       # Left
d.extend([5, 6])
d.extendleft([-1, -2])
d.rotate(1)       # Rotate right
d.rotate(-1)      # Rotate left

# Use cases: queue, stack, sliding window, BFS
```

### `OrderedDict`
```python
from collections import OrderedDict

# Python 3.7+: regular dict preserves insertion order
# OrderedDict still useful for:
# - move_to_end(key, last=True)
# - popitem(last=True) — LIFO
# - Equality considers order
```

### `ChainMap`
```python
from collections import ChainMap

# Layered mappings (config layers)
defaults = {"color": "blue", "size": 10}
user = {"size": 12}
env = {"color": "red"}

config = ChainMap(env, user, defaults)
config["color"]  # "red" (first match)
config["size"]   # 12

# Mutable — writes go to first mapping
config["new"] = "value"  # Added to env
```

### `UserDict`, `UserList`, `UserString`
```python
from collections import UserDict

class ValidatedDict(UserDict):
    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("Keys must be strings")
        super().__setitem__(key, value)
```

- Subclassable wrappers for built-in types
- Easier than inheriting from `dict`/`list`/`str` directly

---

## Decision Rules

| Need | Type |
|------|------|
| Immutable record with names | `NamedTuple` |
| Mutable record with methods | `@dataclass` |
| Auto-create missing keys | `defaultdict` |
| Count hashable items | `Counter` |
| Queue (FIFO) | `deque` |
| Stack (LIFO) | `list` or `deque` |
| Bounded buffer | `deque(maxlen=N)` |
| Sliding window | `deque(maxlen=N)` |
| Layered config | `ChainMap` |
| Custom dict behavior | `UserDict` |
| LRU cache | `functools.lru_cache` (not collections) |

---

## Preferred Patterns

```python
# Frequency analysis
def top_words(text: str, n: int = 10) -> list[tuple[str, int]]:
    words = re.findall(r"\w+", text.lower())
    return Counter(words).most_common(n)

# Sliding window average
def moving_avg(values: list[float], window: int) -> list[float]:
    from collections import deque
    d = deque(maxlen=window)
    result = []
    for v in values:
        d.append(v)
        if len(d) == window:
            result.append(sum(d) / window)
    return result

# Config with layers
def load_config() -> ChainMap:
    return ChainMap(
        os.environ,           # Highest priority
        read_yaml("config.yaml"),
        DEFAULTS,             # Lowest priority
    )
```

---

## Avoid

- `OrderedDict` when regular `dict` works (Python 3.7+)
- `namedtuple` (legacy) — use `NamedTuple` from `typing`
- `ChainMap` for deep nesting (only looks at first level)
- `deque` for random access (O(n)) — use `list`
- `Counter` for non-hashable items

---

## Validation Considerations

- Type checkers understand `NamedTuple`, `TypedDict` better than `namedtuple`
- `Counter` arithmetic returns new `Counter`
- `defaultdict` converts to regular `dict` via `dict(dd)`

---

## Related Skills

- `core/data_structures.md`
- `core/oop.md` (dataclasses)
- `stdlib/itertools.md`
- `generation/type_hints.md`