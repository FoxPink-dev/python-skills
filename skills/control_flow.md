# Core: Control Flow

**Purpose**: Python control flow constructs and patterns.

**When to use**: Always active. Foundation for logic implementation.

---

## Core Rules

### Conditionals
```python
if condition:
    ...
elif other_condition:
    ...
else:
    ...
```

- No parentheses required around condition
- `elif` not `else if`
- Truthiness: `None`, `False`, `0`, `0.0`, `""`, `[]`, `{}`, `set()` are falsy
- Use explicit comparisons (`is None`, `== 0`, `== ""`) when falsy is a valid value

### Ternary Expression
```python
value = true_expr if condition else false_expr
```
- Single expression, not statement
- Use for simple assignments only

### Match Statement (Python 3.10+)
```python
match value:
    case pattern1:
        ...
    case pattern2 if guard:
        ...
    case _:
        ...
```
- Structural pattern matching
- Use for complex data structure dispatch
- Guard clauses with `if`

---

## Loops

### For Loop (Iteration)
```python
for item in iterable:
    ...
else:           # executes if loop completes without break
    ...
```
- `else` clause runs on normal completion (no `break`)
- Preferred over index-based loops

### While Loop
```python
while condition:
    ...
else:
    ...
```
- `else` runs when condition becomes false (no `break`)

### Loop Control
- `break` — exit loop immediately
- `continue` — skip to next iteration
- `pass` — placeholder (no-op)

### Enumerate and Zip
```python
for i, item in enumerate(iterable, start=1):
    ...

for a, b in zip(list1, list2, strict=True):  # Python 3.10+
    ...
```
- `strict=True` raises `ValueError` if lengths differ (Python 3.10+)

---

## Exception Control Flow

```python
try:
    risky_operation()
except SpecificError as e:
    handle(e)
except (Error1, Error2) as e:
    handle(e)
else:           # runs if no exception
    success_path()
finally:        # always runs
    cleanup()
```

- Order: specific exceptions first, general last
- `else` block for code that should only run on success
- `finally` for cleanup (files, locks, connections)

---

## Decision Rules

| Situation | Construct |
|-----------|-----------|
| Simple branch | `if/elif/else` |
| Value-based dispatch (3.10+) | `match/case` |
| Iterate known collection | `for` |
| Iterate with index | `enumerate()` |
| Iterate multiple aligned collections | `zip(strict=True)` |
| Unknown iteration count | `while` |
| Early exit on condition | `break` |
| Skip iteration | `continue` |
| Cleanup always | `finally` |
| Success-only path | `else` on `try` |

---

## Preferred Patterns

```python
# EAFP (Easier to Ask Forgiveness than Permission)
try:
    value = mapping[key]
except KeyError:
    value = default

# LBYL (Look Before You Leap) - when appropriate
if key in mapping:
    value = mapping[key]
else:
    value = default

# Loop with else for search
for item in items:
    if condition(item):
        found = item
        break
else:
    found = default
```

---

## Avoid

- Deeply nested conditionals (refactor to functions/early returns)
- `for i in range(len(list))` — use `enumerate` or direct iteration
- `while True` with `break` when `for` or `itertools` works
- Catching `Exception` or bare `except:` (see error_handling.md)
- Using exceptions for normal control flow (except EAFP patterns)
- Complex logic in ternary expressions

---

## Validation Considerations

- Linters catch unreachable code after `return`/`break`/`continue`
- Type checkers verify exhaustive `match` (with `assert_never`)
- Coverage tools reveal untested branches

---

## Related Skills

- `core/functions.md` (early returns)
- `generation/error_handling.md`
- `generation/async_concurrency.md` (async for/while)
- `anti_patterns/index.md`