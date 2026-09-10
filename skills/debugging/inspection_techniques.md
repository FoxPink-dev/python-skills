---
name: inspection_techniques
purpose: Tools and techniques for runtime inspection and debugging.
category: debugging
triggers:
  - inspect
  - debug
  - pdb
  - breakpoint
  - trace
  - profile
dependencies: []
related: []
priority: supporting
estimated_tokens: 1212
---
# Debugging: Inspection Techniques

**Purpose**: Tools and techniques for runtime inspection and debugging.

**When to use**: Investigating bugs, understanding code behavior, profiling.

---

## Core Rules

### Runtime Inspection

#### Object Inspection
```python
# Type and attributes
type(obj)
dir(obj)
vars(obj)           # __dict__
hasattr(obj, 'attr')
getattr(obj, 'attr', default)
isinstance(obj, Type)
issubclass(cls, Type)

# Function inspection
import inspect
inspect.signature(func)
inspect.getsource(func)
inspect.getfile(func)
inspect.getmodule(func)
inspect.iscoroutinefunction(func)
inspect.isgeneratorfunction(func)
```

#### Frame Inspection
```python
import sys

# Current frame
frame = sys._getframe()
frame.f_locals      # Local variables
frame.f_globals     # Global variables
frame.f_code        # Code object
frame.f_lineno      # Line number

# Call stack
traceback.print_stack()
traceback.extract_stack()

# In exception handler
import traceback
traceback.print_exc()
traceback.format_exc()
```

#### Object Graph
```python
import gc

# Find referrers (what references this object)
gc.get_referrers(obj)

# Find referents (what this object references)
gc.get_referents(obj)

# All objects of type
[obj for obj in gc.get_objects() if isinstance(obj, MyClass)]
```

### Profiling

#### Time Profiling
```bash
# cProfile
python -m cProfile -o profile.stats script.py
# Analyze
python -m pstats profile.stats
# Sort by cumulative time, show top 20
# pstats> sort cumulative
# pstats> stats 20
```

```python
# In code
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# ... code to profile ...

profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(20)
```

#### Memory Profiling
```bash
# memray (modern, fast)
pip install memray
memray run script.py
memray flamegraph memray-results.bin

# objgraph (object counts)
pip install objgraph
python -c "import objgraph; objgraph.show_most_common_types()"
```

#### Line Profiling
```bash
# kernprof
pip install line_profiler
kernprof -l -v script.py
```

### Logging for Debugging
```python
import logging

# Structured debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
)

# Context-specific logger
logger = logging.getLogger("myapp.debug")

# Conditional debug
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("Expensive debug: %s", expensive_computation())
```

### REPL Debugging
```python
# In code
breakpoint()
# Python 3.7+ opens pdb at this line
# In pdb: p var, pp var, n, s, c, l, where, up, down

# Or embed IPython
import IPython
IPython.embed()  # Rich REPL with syntax highlighting
```

### Async Debugging
```python
# Check running tasks
async def debug_tasks():
    for task in asyncio.all_tasks():
        print(task.get_name(), task.get_coro())
    
    # Current task
    current = asyncio.current_task()
    print(current.get_stack())

# Trace async calls
import asyncio
asyncio.set_debug(True)
# Or
loop = asyncio.get_event_loop()
loop.set_debug(True)
```

### Network Debugging
```bash
# HTTP traffic
mitmproxy  # Interactive
mitmdump   # Scriptable

# Or in Python
import http.client
http.client.HTTPConnection.debuglevel = 1

# requests
import logging
logging.getLogger("urllib3").setLevel(logging.DEBUG)
```

### Database Debugging
```python
# SQLAlchemy
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
# Shows all SQL with parameters

# Or echo
engine = create_engine("postgresql://...", echo=True)
```

---

## Decision Rules

| Need | Tool |
|------|------|
| Quick variable check | `breakpoint()` / `print()` |
| Performance bottleneck | `cProfile` / `memray` |
| Memory leak | `memray` / `objgraph` |
| Async deadlock | `asyncio` debug + task inspection |
| SQL query issues | SQLAlchemy echo |
| HTTP issues | `mitmproxy` / request logging |
| Object lifecycle | `gc` / `weakref` |

---

## Preferred Patterns

```python
# Debug helper
def debug_obj(obj, name="obj"):
    print(f"=== {name} ===")
    print(f"Type: {type(obj)}")
    print(f"Dir: {[a for a in dir(obj) if not a.startswith('_')]}")
    if hasattr(obj, '__dict__'):
        print(f"Dict: {vars(obj)}")
    print(f"=== end {name} ===")

# Usage
debug_obj(user, "user")
```

---

## Avoid

- `print()` in production code
- Leaving `breakpoint()` in committed code
- Profiling in production without sampling
- `gc.get_objects()` in hot paths (slow)
- Modifying `sys.path` at runtime

---

## Validation Considerations

- Debug code removed before commit
- Profiling overhead acceptable
- Logs don't contain secrets
- Async debug doesn't change timing significantly

---

## Related Skills

- `debugging/root_cause.md`
- `debugging/common_bugs.md`
- `stdlib/logging.md`
- `generation/async_concurrency.md`