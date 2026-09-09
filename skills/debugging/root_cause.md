# Debugging: Root Cause Analysis

**Purpose**: Systematic approach to finding and fixing bugs.

**When to use**: Any bug investigation.

---

## Core Rules

### Debugging Process
```
1. REPRODUCE — Create minimal failing case
2. ISOLATE — Narrow down location
3. HYPOTHESIZE — Form theory of cause
4. TEST HYPOTHESIS — Verify with experiment
5. FIX — Minimal change addressing root cause
6. REGRESSION TEST — Prevent recurrence
7. DOCUMENT — Record for future
```

### Reproduction
```python
# Minimal reproduction script
# reproduce_issue.py
import sys
sys.path.insert(0, "src")

from mypackage import process

# Exact input that fails
input_data = load_failing_case()

try:
    result = process(input_data)
    print("UNEXPECTED SUCCESS:", result)
except Exception as e:
    print(f"REPRODUCED: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
```

### Isolation Techniques

#### Binary Search (Git Bisect)
```bash
# Find commit that introduced bug
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
# Git checks out middle commit
# Run tests: pytest test_failing.py
# git bisect good/bad
# Repeats until found
```

#### Print Debugging (Structured)
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or structured
import structlog
log = structlog.get_logger()

def problematic_function(data):
    log.debug("enter", data_keys=list(data.keys()))
    result = step1(data)
    log.debug("after_step1", result=result)
    result = step2(result)
    log.debug("after_step2", result=result)
    return result
```

#### Interactive Debugger
```python
# In code
breakpoint()  # Python 3.7+

# Or conditional
if condition:
    breakpoint()

# Run: python -m pdb script.py
# Commands: n (next), s (step), c (continue), p (print), l (list)
```

### Common Bug Patterns

| Pattern | Symptoms | Investigation |
|---------|----------|---------------|
| Off-by-one | First/last element wrong | Check loop bounds, slice indices |
| Mutable default | State leaks between calls | Check function defaults |
| Race condition | Intermittent, timing-dependent | Add logging, check thread safety |
| Null reference | AttributeError/TypeError | Trace None propagation |
| Type mismatch | Unexpected type at runtime | Add type checks, check boundaries |
| Resource leak | Slow degradation, OOM | Check cleanup in finally/with |
| Encoding issue | Unicode errors, corrupt data | Check encode/decode boundaries |

### Hypothesis Testing
```python
# Hypothesis: "The bug is in validate_email()"
# Test: Call validate_email() directly with failing input

def test_hypothesis():
    failing_email = "USER@EXAMPLE.COM"
    result = validate_email(failing_email)
    # If this fails → hypothesis confirmed
    # If this passes → bug is elsewhere
```

### Fixing Root Cause
```python
# BAD — symptom fix
def process(data):
    if data is None:  # Handles symptom
        return default()
    return real_process(data)

# GOOD — root cause fix
def get_data() -> Data:
    # Fix upstream to never return None
    data = fetch()
    if data is None:
        raise DataNotFoundError()  # Explicit failure
    return data

def process(data: Data) -> Result:  # Type hint documents non-None
    return real_process(data)
```

### Regression Test
```python
# Always add test for the exact bug
def test_issue_123_uppercase_email_normalized():
    """Regression: Issue #123 - uppercase email caused duplicate"""
    user = create_user("USER@EXAMPLE.COM", "Test")
    assert user.email == "user@example.com"
```

---

## Decision Rules

| Bug Type | First Step |
|----------|------------|
| Crash | Get traceback, reproduce |
| Wrong output | Create minimal input |
| Performance | Profile, find bottleneck |
| Intermittent | Add extensive logging |
| Security | Isolate, assess impact |

---

## Preferred Patterns

```python
# Debug context manager
from contextlib import contextmanager

@contextmanager
def debug_context(name: str):
    log.debug(f"{name}: start")
    try:
        yield
    except Exception as e:
        log.debug(f"{name}: error", error=str(e))
        raise
    else:
        log.debug(f"{name}: success")

with debug_context("process_order"):
    result = process_order(order)
```

---

## Avoid

- Fixing without reproducing
- Guessing instead of isolating
- Fixing symptoms, not root cause
- No regression test
- Large changes to fix small bug

---

## Validation Considerations

- Bug reproduced before fix
- Fix verified with reproduction case
- Regression test added
- Related tests still pass
- No similar bugs elsewhere (grep for pattern)

---

## Related Skills

- `debugging/common_bugs.md`
- `debugging/inspection_techniques.md`
- `testing/regression_tests.md`
- `generation/error_handling.md`