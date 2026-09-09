# Anti-Patterns: Index

**Purpose**: Prevent generation of known anti-patterns. This is the master reference.

**When to use**: Always active. Check before and during code generation.

---

## Quick Reference

| Category | Anti-Pattern | Prevention |
|----------|--------------|------------|
| **Exceptions** | Bare `except:` / `except Exception:` | Catch specific exceptions only |
| **Exceptions** | Swallowed exceptions | Log or re-raise, never silent |
| **Arguments** | Mutable default arguments | Use `None` sentinel pattern |
| **State** | Unnecessary global state | Use dependency injection |
| **Dependencies** | Unnecessary dependencies | Stdlib first, existing deps second |
| **Inheritance** | Excessive inheritance | Prefer composition |
| **Abstraction** | Premature abstraction | Wait for 3+ use cases (Rule of Three) |
| **Functions** | Giant functions (>50 lines) | Extract to smaller functions |
| **Classes** | God classes | Single responsibility, split |
| **Duplication** | Duplicated logic | Extract (true duplication only) |
| **Cleverness** | Unreadable one-liners | Prefer explicit, readable code |
| **Comprehensions** | Unnecessary/overly complex | Use loops for complex logic |
| **Async** | Premature async | Only for I/O-bound concurrency |
| **Optimization** | Premature optimization | Profile first, optimize bottlenecks |
| **Secrets** | Hardcoded secrets | Environment variables, secret managers |
| **Subprocess** | Unsafe subprocess usage | List form, no `shell=True`, allowlist |
| **Deserialization** | Unsafe deserialization | `json`, `yaml.safe_load`, never `pickle` |
| **SQL** | SQL injection | Parameterized queries only |
| **Files** | Insecure temp files | `tempfile`, validate paths |
| **Eval/Exec** | Unnecessary `eval`/`exec` | Never for untrusted input |

---

## Detailed Patterns

### 1. Bare Except
```python
# ANTI-PATTERN
try:
    risky()
except:
    pass  # Catches KeyboardInterrupt, SystemExit!

try:
    risky()
except Exception:
    pass  # Swallows all errors silently

# CORRECT
try:
    risky()
except SpecificError:
    handle()
except AnotherError:
    handle()
```

### 2. Mutable Default Arguments
```python
# ANTI-PATTERN
def func(items=[]):
    items.append(1)
    return items

# CORRECT
def func(items=None):
    if items is None:
        items = []
    items.append(1)
    return items
```

### 3. Global Mutable State
```python
# ANTI-PATTERN
cache = {}

def get_data(key):
    if key not in cache:
        cache[key] = fetch(key)
    return cache[key]

# CORRECT
class DataService:
    def __init__(self):
        self._cache = {}
    
    def get_data(self, key):
        if key not in self._cache:
            self._cache[key] = fetch(key)
        return self._cache[key]

# Inject instance where needed
```

### 4. Swallowed Exceptions
```python
# ANTI-PATTERN
try:
    save(user)
except:
    pass  # User not saved, no indication!

# CORRECT
try:
    save(user)
except DatabaseError as e:
    logger.error("Failed to save user", extra={"user_id": user.id, "error": str(e)})
    raise SaveFailedError() from e
```

### 5. Unnecessary Dependencies
```python
# ANTI-PATTERN — adding `requests` for one HTTP call
# when `urllib` or `http.client` in stdlib works

# CORRECT — evaluate need
# If simple GET: urllib.request
# If complex: requests/httpx justified
```

### 6. Excessive Inheritance
```python
# ANTI-PATTERN
class Base:
    def a(self): ...
    def b(self): ...

class A(Base): ...
class B(A): ...
class C(B): ...
class D(C): ...  # 4 levels!

# CORRECT — composition
class Service:
    def __init__(self, a: A, b: B, c: C):
        self.a = a
        self.b = b
        self.c = c
```

### 7. Premature Abstraction
```python
# ANTI-PATTERN — abstracting after 1 use
def process_user(user):
    validate(user)
    save(user)
    notify(user)

def process_order(order):
    validate(order)
    save(order)
    notify(order)

# Abstracted to:
def process(entity):  # WRONG - different validation!
    validate(entity)
    save(entity)
    notify(entity)

# CORRECT — wait for 3rd use case with SAME pattern
```

### 8. Giant Functions
```python
# ANTI-PATTERN
def process_everything(data):
    # 200 lines of validation, calculation, persistence, notification
    ...

# CORRECT
def validate(data): ...
def calculate(data): ...
def persist(data): ...
def notify(data): ...

def process(data):
    validate(data)
    result = calculate(data)
    persist(result)
    notify(result)
```

### 9. God Classes
```python
# ANTI-PATTERN
class UserManager:
    def create(self): ...
    def delete(self): ...
    def update(self): ...
    def get(self): ...
    def list(self): ...
    def send_email(self): ...
    def generate_report(self): ...
    def backup(self): ...
    def migrate(self): ...
    # 20+ methods, multiple responsibilities

# CORRECT
class UserRepository: ...
class UserService: ...
class EmailService: ...
class ReportGenerator: ...
class BackupService: ...
```

### 10. Clever One-Liners
```python
# ANTI-PATTERN
result = [x for y in data for x in y.split() if x.isalnum() and len(x) > 2]

# CORRECT
result = []
for item in data:
    for word in item.split():
        if word.isalnum() and len(word) > 2:
            result.append(word)
```

### 11. Premature Async
```python
# ANTI-PATTERN
async def process(data):  # No I/O, just CPU
    return compute(data)

# CORRECT — sync for CPU-bound
def process(data):
    return compute(data)

# CORRECT — async for I/O-bound
async def fetch_data(url):
    async with httpx.AsyncClient() as client:
        return await client.get(url)
```

### 12. Premature Optimization
```python
# ANTI-PATTERN
# Using complex caching for 10 items
# Using C extension for simple loop
# Pre-computing everything at startup

# CORRECT
# Profile first
# Optimize measured bottlenecks
# Keep simple until proven necessary
```

### 13. Hardcoded Secrets
```python
# ANTI-PATTERN
API_KEY = "sk_live_abc123"
DB_PASSWORD = "secret123"

# CORRECT
import os
API_KEY = os.getenv("API_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")
```

### 14. Unsafe Subprocess
```python
# ANTI-PATTERN
subprocess.run(f"process {user_input}", shell=True)

# CORRECT
subprocess.run(["process", user_input], check=True)
```

### 15. Unsafe Deserialization
```python
# ANTI-PATTERN
import pickle
data = pickle.loads(untrusted_bytes)  # RCE!

import yaml
data = yaml.load(untrusted_string)  # RCE!

# CORRECT
import json
data = json.loads(untrusted_string)

import yaml
data = yaml.safe_load(untrusted_string)
```

### 16. SQL Injection
```python
# ANTI-PATTERN
cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")

# CORRECT
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

### 17. Insecure Temp Files
```python
# ANTI-PATTERN
with open("/tmp/myfile.txt", "w") as f:  # Predictable, race condition
    f.write(secret)

# CORRECT
import tempfile
with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
    f.write(secret)
# Or
with tempfile.TemporaryDirectory() as tmpdir:
    path = Path(tmpdir) / "file.txt"
    path.write_text(secret)
```

### 18. Unnecessary Eval/Exec
```python
# ANTI-PATTERN
result = eval(user_input)  # RCE!
exec(user_code)  # RCE!

# CORRECT
# Never eval/exec untrusted input
# Use proper parsing (json, ast.literal_eval for safe subset)
import ast
safe = ast.literal_eval(user_input)  # Only literals
```

---

## Validation Checklist (Before Committing Code)

- [ ] No bare `except:` or `except Exception:`
- [ ] No mutable default arguments
- [ ] No global mutable state
- [ ] No swallowed exceptions
- [ ] No unnecessary dependencies added
- [ ] No inheritance >2 levels
- [ ] No abstraction without 3+ use cases
- [ ] No functions >50 lines
- [ ] No classes with >10 public methods
- [ ] No duplicated logic (true duplication)
- [ ] No clever unreadable one-liners
- [ ] No unnecessary comprehensions
- [ ] No async without I/O
- [ ] No optimization without profiling
- [ ] No hardcoded secrets
- [ ] No `shell=True` with user input
- [ ] No `pickle`/`yaml.load` on untrusted data
- [ ] No string interpolation in SQL
- [ ] No predictable temp file names
- [ ] No `eval`/`exec` on untrusted input

---

## Enforcement

```bash
# Ruff rules that catch many
ruff check .
# B001: bare except
# B006: mutable default argument
# B007: loop variable in closure
# B008: function call in default arg
# B009: unused loop variable
# B010: redundant exception caught
# B011: assert in non-test
# B012: mutable class attribute
# B014: unnecessary list comp
# B015: unnecessary set comp
# B016: unnecessary dict comp
# B017: unnecessary generator
# B018: unnecessary ternary
# B019: unnecessary lambda
# S101: assert in test (OK in tests)
# S102: exec
# S103: eval
# S104: hardcoded password
# S105: hardcoded password in string
# S106: hardcoded password in config
# S107: hardcoded password in command
# S108: hardcoded tmp directory
# S109: hardcoded password in function call
# S601: shell=True
# S602: shell=True with variable
# S603: shell=True with input
# S604: shell=True with user input
# S605: shell=True with command
# S606: shell=True with user input
# S607: shell=True with variable
# S608: SQL injection
# S609: SQL injection
# S610: shell=True with variable
```

---

## Related Skills

All skills reference anti-patterns. Key connections:
- `generation/error_handling.md` (exceptions)
- `core/functions.md` (mutable defaults)
- `quality/abstractions.md` (premature abstraction)
- `quality/functions.md` (giant functions)
- `quality/duplication.md` (duplication)
- `generation/async_concurrency.md` (premature async)
- `security/*` (secrets, injection, deserialization)
- `debugging/common_bugs.md` (common bug patterns)