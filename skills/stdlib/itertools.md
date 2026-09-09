# Stdlib: itertools

**Purpose**: Efficient iteration tools for combinatorics and data processing.

**When to use**: Complex iteration patterns, avoiding manual loops.

---

## Core Rules

### Infinite Iterators
```python
import itertools

itertools.count(start=0, step=1)      # 0, 1, 2, ...
itertools.cycle(iterable)             # Repeat forever
itertools.repeat(elem, times=None)    # Repeat elem (forever if times=None)
```

### Finite Iterators (Combinatorics)
```python
# Cartesian product
itertools.product("AB", repeat=2)     # AA, AB, BA, BB
itertools.product(range(3), "AB")     # (0,A), (0,B), (1,A), ...

# Permutations (order matters)
itertools.permutations("ABCD", 2)     # AB, AC, AD, BA, BC, BD, CA, CB, CD, DA, DB, DC

# Combinations (order doesn't matter)
itertools.combinations("ABCD", 2)     # AB, AC, AD, BC, BD, CD
itertools.combinations_with_replacement("ABCD", 2)  # AA, AB, AC, AD, BB, BC, BD, CC, CD, DD
```

### Filtering Iterators
```python
itertools.filterfalse(pred, iterable)  # Opposite of filter
itertools.takewhile(pred, iterable)    # Until pred false
itertools.dropwhile(pred, iterable)    # Skip while pred true
itertools.compress(data, selectors)    # Data where selector true
itertools.islice(iterable, start, stop, step)  # Slice iterator
```

### Grouping
```python
# Group consecutive items (input MUST be sorted by key)
itertools.groupby(iterable, key=lambda x: x[0])
# Returns (key, group_iterator) — consume group before next iteration!

# Example
data = [("a", 1), ("a", 2), ("b", 3), ("a", 4)]
for key, group in itertools.groupby(data, key=lambda x: x[0]):
    print(key, list(group))
# a [(a,1), (a,2)]
# b [(b,3)]
# a [(a,4)]  # Separate group!
```

### Accumulation
```python
itertools.accumulate(iterable, func=operator.add)
# Running totals: [1, 2, 3] -> 1, 3, 6
itertools.accumulate([1,2,3], func=operator.mul)  # 1, 2, 6
itertools.accumulate([1,2,3], initial=10)         # 10, 11, 13, 16 (Python 3.8+)
```

### Merging/Transforming
```python
itertools.chain(*iterables)              # Flatten: chain(a, b, c)
itertools.chain.from_iterable(iterable)  # Flatten nested
itertools.zip_longest(*iterables, fillvalue=None)  # Pad shorter
itertools.pairwise(iterable)             # (s0,s1), (s1,s2), ... (Python 3.10+)
itertools.starmap(func, iterable)        # func(*args) for each item
```

### Recipes (from docs)
```python
def batched(iterable, n):
    "Batch data into tuples of length n. The last batch may be shorter."
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch

def sliding_window(iterable, n):
    "Return a sliding window of width n over the iterable."
    it = iter(iterable)
    window = collections.deque(itertools.islice(it, n-1), maxlen=n)
    for x in it:
        window.append(x)
        yield tuple(window)

def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    num_active = len(iterables)
    nexts = cycle(iter(it).__next__ for it in iterables)
    while num_active:
        try:
            for next_func in nexts:
                yield next_func()
        except StopIteration:
            num_active -= 1
            nexts = cycle(itertools.islice(nexts, num_active))
```

---

## Decision Rules

| Need | Tool |
|------|------|
| All combinations | `product` |
| Ordered selections | `permutations` |
| Unordered selections | `combinations` |
| Unordered with replacement | `combinations_with_replacement` |
| Skip prefix | `dropwhile` / `islice` |
| Take prefix | `takewhile` / `islice` |
| Group consecutive | `groupby` (sort first!) |
| Running totals | `accumulate` |
| Flatten sequences | `chain` / `chain.from_iterable` |
| Parallel iteration with padding | `zip_longest` |
| Adjacent pairs | `pairwise` (3.10+) |
| Batch processing | `batched` recipe / `itertools.batched` (3.12+) |

---

## Preferred Patterns

```python
# Chunk processing
for batch in batched(large_iterable, 1000):
    process_batch(batch)

# Pairwise comparison
for a, b in itertools.pairwise(sorted_data):
    if b - a > threshold:
        ...

# Cartesian product for parameter grids
for params in itertools.product(learning_rates, batch_sizes, optimizers):
    train(*params)

# Consuming groupby correctly
for key, group in itertools.groupby(sorted_data, key=keyfunc):
    group_list = list(group)  # Must consume before next iteration
    process_group(key, group_list)
```

---

## Avoid

- `groupby` on unsorted data (produces incorrect groups)
- Converting large iterators to lists unnecessarily
- `zip_longest` without considering `fillvalue` semantics
- Manual index management when `islice`, `enumerate`, `pairwise` exist
- Nested `product` when single `product` with multiple iterables works

---

## Python 3.12+ Additions

```python
itertools.batched(iterable, n)  # Built-in batching
itertools.chunked(iterable, n)  # Alias for batched
```

---

## Validation Considerations

- All return iterators (lazy)
- Type checkers understand generic types
- `groupby` groups are iterators — consume immediately

---

## Related Skills

- `core/data_structures.md`
- `core/advanced_python.md` (generators)
- `stdlib/collections.md`
- `stdlib/functools.md`