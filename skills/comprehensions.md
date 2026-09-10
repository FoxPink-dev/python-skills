---
name: comprehensions
purpose: Python comprehension syntax and appropriate usage.
category: skills
triggers:
  - comprehension
  - list-comp
  - dict-comp
  - set-comp
  - generator-expression
dependencies: []
related: []
priority: supporting
estimated_tokens: 1000
---
# Core: Comprehensions

**Purpose**: Python comprehension syntax and appropriate usage.

**When to use**: Transforming, filtering, or creating collections.

---

## Core Rules

### List Comprehension
```python
# Basic
squares = [x * x for x in range(10)]

# With filter
evens = [x for x in range(10) if x % 2 == 0]

# Nested (cartesian product)
pairs = [(x, y) for x in range(3) for y in range(3)]
# [(0,0), (0,1), (0,2), (1,0), ...]

# With conditional expression (ternary)
labels = ["even" if x % 2 == 0 else "odd" for x in range(10)]
```

### Dict Comprehension
```python
# Basic
name_to_len = {name: len(name) for name in names}

# With filter
short_names = {name: len(name) for name in names if len(name) < 5}

# Swap keys/values (values must be unique)
inverted = {v: k for k, v in mapping.items()}

# From two sequences
mapping = {k: v for k, v in zip(keys, values, strict=True)}
```

### Set Comprehension
```python
unique_lengths = {len(name) for name in names}
```

### Generator Expression
```python
# Lazy, memory efficient
squares_gen = (x * x for x in range(1_000_000))

# Consume
for sq in squares_gen:
    ...

# Or convert
list(squares_gen)
```

---

## Walrus Operator (Python 3.8+)
```python
# Assign and use in comprehension
results = [y for x in data if (y := compute(x)) is not None]

# In while loops
while (line := file.readline()) != '':
    process(line)
```

---

## Decision Rules

| Situation | Choice |
|-----------|--------|
| Simple transform + filter | Comprehension |
| Multiple transforms, complex logic | Explicit `for` loop |
| Need to debug intermediate values | Explicit `for` loop |
| Large/unknown size, memory concern | Generator expression |
| Dict from two parallel sequences | `{k: v for k, v in zip(...)}` |
| Flatten nested list | `[item for sublist in nested for item in sublist]` |

---

## Preferred Patterns

```python
# Flatmap pattern
flattened = [item for sublist in nested for item in sublist]

# Grouping with defaultdict (clearer than comprehension)
from collections import defaultdict
grouped = defaultdict(list)
for item in items:
    grouped[key(item)].append(item)

# Set for deduplication preserving order (Python 3.7+)
seen = set()
unique = [x for x in items if not (x in seen or seen.add(x))]
# Or simpler (loses order): list(set(items))

# Chained operations — prefer explicit loop
result = []
for item in items:
    transformed = transform(item)
    if validate(transformed):
        result.append(transformed)
```

---

## Avoid

- Nested comprehensions >2 levels deep (unreadable)
- Side effects in comprehensions (mutating external state)
- Complex conditional expressions (ternary) in comprehensions
- Generator expressions passed directly to functions that consume immediately (just use list comprehension)
- Walrus operator for trivial assignments (reduces readability)
- Comprehensions spanning multiple lines without clear structure

---

## Anti-Patterns

```python
# BAD: Side effect
[x.append(i) for i in range(10)]  # Returns [None, None, ...]

# BAD: Too complex
result = [
    transform(x) 
    for x in items 
    if (cond1 := check1(x)) 
    and (cond2 := check2(x) if cond1 else False)
    for y in related(x)
]

# GOOD: Explicit loop
result = []
for x in items:
    if not check1(x):
        continue
    if not check2(x):
        continue
    for y in related(x):
        result.append(transform(x))
```

---

## Validation Considerations

- Type checkers infer comprehension types
- Linters flag overly complex comprehensions
- Memory profile for large comprehensions vs generators

---

## Related Skills

- `core/data_structures.md`
- `core/advanced_python.md` (generators)
- `generation/type_hints.md`
- `quality/readability.md`
- `anti_patterns/index.md`