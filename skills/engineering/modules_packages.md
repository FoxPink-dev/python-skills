# Engineering: Modules and Packages

**Purpose**: Python module system, imports, and package organization.

**When to use**: Structuring code, managing imports, avoiding circular dependencies.

---

## Core Rules

### Module vs Package
- **Module**: Single `.py` file
- **Package**: Directory with `__init__.py` (regular) or without (namespace, 3.3+)

### Import Styles
```python
# Absolute (preferred)
from package.module import Class
from package import module

# Relative (within package only)
from .module import Class
from ..parent import Class
from ... import top_level

# Import module (not names)
import package.module
package.module.function()

# Avoid
from module import *  # Pollutes namespace, unclear dependencies
```

### `__init__.py` Responsibilities
```python
# 1. Define public API
from .core import main_function
from .models import User

__all__ = ["main_function", "User"]

# 2. Optional: convenient imports
from .subpackage import feature  # Re-export

# 3. Optional: version
try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0"

# 4. Optional: initialization
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
```

### Private Modules
```python
# _private.py — convention: not part of public API
# __init__.py should not import from _private in __all__

# __dunder__.py — special Python modules (avoid creating)
```

### Namespace Packages (PEP 420)
```python
# No __init__.py — multiple directories contribute to same package
# pkg_resources / importlib.metadata handles this
# Use for plugins, large orgs splitting packages
```

---

## Circular Import Prevention

### Causes
```python
# a.py
from b import B
class A: pass

# b.py
from a import A
class B: pass
```

### Solutions
1. **Refactor** — move shared code to third module
2. **Lazy import** — import inside function
3. **Type-only import** — `from __future__ import annotations` + `TYPE_CHECKING`
4. **Interface/Protocol** — depend on abstraction

```python
# Type-only import (no runtime dependency)
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .other import OtherClass

def func(obj: OtherClass) -> None:  # Only for type checking
    ...
```

---

## Import Best Practices

```python
# Standard library first
import os
import sys
from pathlib import Path
from typing import Optional

# Third party
import requests
from pydantic import BaseModel

# Local (absolute)
from mypackage.core import process
from mypackage.models import User

# Local (relative) — only within same package
from . import utils
from ..config import settings
```

### Import Order (per PEP 8 / ruff)
1. Standard library
2. Third party
3. Local (absolute)
4. Local (relative)

---

## Dynamic Imports
```python
import importlib

# Import by name
module = importlib.import_module("package.module")
Class = getattr(module, "ClassName")

# Plugin pattern
def load_plugins(entry_point: str) -> list[Plugin]:
    plugins = []
    for ep in importlib.metadata.entry_points(group=entry_point):
        plugins.append(ep.load())
    return plugins
```

---

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| `import *` | Pollutes namespace, unclear deps | Explicit imports |
| Deep relative imports | Hard to read, fragile | Use absolute imports |
| `sys.path` modification | Non-portable, fragile | Use proper packaging |
| Dynamic imports for perf-critical paths | Import overhead | Use static imports |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| `import *` | Namespace pollution, unclear deps | Explicit imports |
| Circular imports | `ImportError` | Refactor to third module |
| `sys.path` hacking | Non-portable, fragile | Use proper packaging |
| Import side effects | Unexpected behavior on import | Keep imports clean |
| Deep relative imports | Hard to read, fragile | Use absolute imports |

### Anti-Pattern

```python
# NEVER: import * from module
from module import *  # What's imported? Nobody knows

# NEVER: sys.path modification
import sys
sys.path.insert(0, "/path/to/package")  # Non-portable

# NEVER: Deep relative imports
from ... import top_level  # Hard to read

# BETTER: Absolute imports
from package.module import Class
```

| Situation | Approach |
|-----------|----------|
| Public API | Define in `__init__.py` with `__all__` |
| Internal helper | Prefix with `_` (module or name) |
| Type-only dependency | `TYPE_CHECKING` guard |
| Plugin/extension | `importlib.metadata` entry points |
| Optional dependency | `try/except ImportError` |

---

## Preferred Patterns

```python
# Optional dependency
try:
    import orjson as json
except ImportError:
    import json

# Protocol for external dependency
class Cache(Protocol):
    def get(self, key: str) -> bytes | None: ...
    def set(self, key: str, value: bytes) -> None: ...

# Usage doesn't require import
def process(cache: Cache) -> None:
    ...
```

---

## Avoid

- `import *` (except `__all__` in `__init__.py`)
- Relative imports beyond one level (`from .... import`)
- Modifying `sys.path` at runtime
- Import side effects (code running on import)
- Circular imports (refactor instead)

---

## Validation Considerations

- `python -c "import package"` works
- Import time < 100ms (for CLI tools)
- No circular import warnings
- `mypy` passes with `--strict`

---

## Related Skills

- `engineering/project_structure.md`
- `engineering/pyproject_toml.md`
- `generation/type_hints.md` (TYPE_CHECKING)
- `generation/protocols_generics.md` (Protocol)