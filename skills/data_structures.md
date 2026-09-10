---
name: data_structures
purpose: Python built-in data structures and their appropriate use.
category: skills
triggers:
  - list
  - dict
  - set
  - tuple
  - deque
  - heap
  - dataclass
  - namedtuple
dependencies: []
related: []
priority: supporting
estimated_tokens: 1293
---
# Core: Data Structures

**Purpose**: Python built-in data structures and their appropriate use.

**When to use**: Always active. Choose the right structure for the problem.

---

## Core Rules

### List (`list`)
- Ordered, mutable, allows duplicates
- O(1) append, pop from end; O(n) insert/pop from front
- Use for sequences where order matters

```python
items: list[str] = ["a", "b", "c"]
items.append("d")
items.extend(["e", "f"])
items.insert(0, "start")
popped = items.pop()      # From end
popped = items.pop(0)     # From front (O(n))
```

### Tuple (`tuple`)
- Ordered, immutable, allows duplicates
- Lightweight, hashable (if contents hashable)
- Use for fixed collections, heterogeneous data, return values

```python
point: tuple[float, float] = (1.0, 2.0)
# Unpacking
x, y = point
# Named tuple alternative
from typing import NamedTuple
class Point(NamedTuple):
    x: float
    y: float
```

### Dict (`dict`)
- Key-value mapping, mutable, keys unique and hashable
- O(1) average lookup, insertion, deletion
- Preserves insertion order (Python 3.7+)

```python
data: dict[str, int] = {"a": 1, "b": 2}
data["c"] = 3
value = data.get("key", default)  # Safe access
value = data.setdefault("key", default)  # Get or set
```

### Set (`set`) / Frozenset (`frozenset`)
- Unordered, unique elements, mutable (`set`) or immutable (`frozenset`)
- O(1) membership testing
- Mathematical set operations

```python
unique: set[int] = {1, 2, 3}
unique.add(4)
unique.update([5, 6])
intersection = unique & {3, 4, 5}
union = unique | {7, 8}
```

---

## Nesting and Composition

```python
# List of dicts
records: list[dict[str, Any]] = [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]

# Dict of lists
grouped: dict[str, list[int]] = {"even": [2, 4], "odd": [1, 3]}

# Complex nesting
matrix: list[list[int]] = [[1, 2], [3, 4]]
```

---

## Indexing and Slicing

```python
seq = [0, 1, 2, 3, 4, 5]

seq[0]      # First
seq[-1]     # Last
seq[1:4]    # Indices 1,2,3
seq[:3]     # First 3
seq[3:]     # From index 3
seq[::2]    # Every 2nd
seq[::-1]   # Reversed
```

- Slicing returns new object (shallow copy)
- Out-of-range slice indices don't raise (clamped)

---

## Unpacking

```python
# Basic
a, b, c = (1, 2, 3)

# Extended (Python 3+)
first, *middle, last = [1, 2, 3, 4, 5]
# first=1, middle=[2,3,4], last=5

# Ignored values
_, _, value = get_triple()

# Dict unpacking (Python 3.5+)
{**dict1, **dict2}          # Merge (later wins)
{**dict1, "new": value}     # Add key
```

---

## Iteration Patterns

```python
# Direct iteration
for item in items:
    ...

# With index
for i, item in enumerate(items):
    ...

# Multiple sequences
for a, b in zip(list1, list2, strict=True):
    ...

# Reverse
for item in reversed(items):
    ...

# Sorted
for item in sorted(items):
    ...

# Dictionary
for key, value in mapping.items():
    ...
for key in mapping:
    ...
for value in mapping.values():
    ...
```

---

## Mutation vs Reassignment

```python
# Mutation (changes object in place)
lst.append(x)
lst.extend(other)
lst[0] = new
dct[key] = value
s.add(item)

# Reassignment (binds name to new object)
lst = lst + [x]        # New list
dct = {**dct, k: v}    # New dict
```

- Mutation affects all references to the object
- Reassignment only affects the local name

---

## Decision Rules

| Need | Structure |
|------|-----------|
| Ordered, mutable, duplicates | `list` |
| Ordered, immutable, hashable | `tuple` / `NamedTuple` |
| Key → value, fast lookup | `dict` |
| Unique items, membership test | `set` |
| Unique items, immutable | `frozenset` |
| Fixed schema, heterogeneous | `dataclass` / `NamedTuple` / `TypedDict` |
| Stack (LIFO) | `list` (append/pop) |
| Queue (FIFO) | `collections.deque` |
| Priority queue | `heapq` |
| Counter/multiset | `collections.Counter` |
| Default values for missing keys | `collections.defaultdict` |
| Ordered dict with LRU | `collections.OrderedDict` / `functools.lru_cache` |

---

## Preferred Patterns

```python
# Use comprehensions for simple transformations
squares = [x*x for x in range(10)]
even_squares = {x*x for x in range(10) if x % 2 == 0}
name_to_len = {name: len(name) for name in names}

# Generator for large/unknown sequences
def generate_items():
    for i in range(1_000_000):
        yield compute(i)

# Defaultdict for grouping
from collections import defaultdict
grouped = defaultdict(list)
for item in items:
    grouped[key(item)].append(item)
```

---

## Avoid

- `list` for membership testing (O(n)) — use `set`
- `list` for queue (pop(0) is O(n)) — use `deque`
- Nested lists for matrices (use `numpy` or flat list)
- `dict` with mutable keys (unhashable)
- Modifying container during iteration (iterate over copy)
- Excessive nesting depth (>3 levels) — use dataclasses

---

## Validation Considerations

- Type checkers verify generic type parameters
- `collections.abc` interfaces for structural typing
- Mutation during iteration raises `RuntimeError`

---

## Related Skills

- `core/advanced_python.md` (generators, iterators)
- `stdlib/collections.md`
- `stdlib/itertools.md`
- `generation/type_hints.md` (generics)
- `core/comprehensions.md`
- `quality/duplication.md`