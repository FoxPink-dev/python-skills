---
name: error_handling
purpose: Consistent, safe error handling patterns for code generation
category: generation
triggers:
  - error
  - exception
  - try
  - except
  - raise
  - result
dependencies:
  - generation/workflow
  - quality/quality_functions
related:
  - security/input_validation
  - testing/regression_tests
  - generation/async_concurrency
  - debugging/common_bugs
priority: critical
estimated_tokens: 2500
---
# Generation: Error Handling

**Purpose**: Consistent, safe error handling patterns for code generation.

**When to use**: All code generation. Error handling is critical for correctness.

---

## Core Rules

### Exception Hierarchy
```
BaseException
├── KeyboardInterrupt
├── SystemExit
├── GeneratorExit
└── Exception
    ├── StopIteration
    ├── StopAsyncIteration
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   └── ...
    ├── AssertionError
    ├── AttributeError
    ├── BufferError
    ├── EOFError
    ├── ImportError
    │   └── ModuleNotFoundError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── MemoryError
    ├── NameError
    │   └── UnboundLocalError
    ├── OSError
    │   ├── BlockingIOError
    │   ├── ChildProcessError
    │   ├── ConnectionError
    │   ├── FileExistsError
    │   ├── FileNotFoundError
    │   ├── InterruptedError
    │   ├── IsADirectoryError
    │   ├── NotADirectoryError
    │   ├── PermissionError
    │   ├── ProcessLookupError
    │   └── TimeoutError
    ├── ReferenceError
    ├── RuntimeError
    │   ├── NotImplementedError
    │   └── RecursionError
    ├── SyntaxError
    │   └── IndentationError
    ├── SystemError
    ├── TypeError
    ├── ValueError
    │   └── UnicodeError
    └── Warning
```

### Catch Specific Exceptions
```python
# GOOD — specific
try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    logger.error("Invalid JSON", extra={"error": str(e), "pos": e.pos})
    raise ValueError("Invalid JSON input") from e

# GOOD — tuple of related
try:
    response = requests.get(url, timeout=5)
except (requests.Timeout, requests.ConnectionError) as e:
    logger.warning("Request failed", extra={"url": url, "error": str(e)})
    raise ServiceUnavailable("Service unreachable") from e

# BAD — bare except
try:
    ...
except:
    ...  # Catches KeyboardInterrupt, SystemExit!

# BAD — broad Exception
try:
    ...
except Exception:
    ...  # Swallows everything, hard to debug
```

### Exception Chaining
```python
# Explicit chaining (preserves original traceback)
try:
    risky()
except OriginalError as e:
    raise NewError("Context") from e

# Implicit chaining (automatic when raising in except)
try:
    risky()
except OriginalError:
    raise NewError("Context")  # __context__ set automatically

# Suppress chaining
try:
    risky()
except OriginalError:
    raise NewError("Context") from None
```

### Custom Exceptions
```python
# Domain-specific exceptions
class DomainError(Exception):
    """Base for domain errors."""
    def __init__(self, message: str, code: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}

class ValidationError(DomainError):
    def __init__(self, field: str, message: str):
        super().__init__(message, "VALIDATION_ERROR", {"field": field})

class NotFoundError(DomainError):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource} not found: {id}", "NOT_FOUND", {"resource": resource, "id": id})

class ConflictError(DomainError):
    pass

# Usage
raise ValidationError("email", "Invalid format")
raise NotFoundError("User", "123")
```

### Error Categories (For Handling Strategy)

| Category | Examples | Handling |
|----------|----------|----------|
| Expected operational failure | `NotFoundError`, `ValidationError`, `ConflictError` | Handle explicitly, return error result |
| Programming bug | `AssertionError`, `TypeError`, `IndexError` | Let crash, fix code |
| Invalid external input | `ValueError`, `JSONDecodeError` | Validate early, return 400 |
| Configuration failure | `KeyError` (missing config), `ImproperlyConfigured` | Fail fast at startup |
| System failure | `OSError`, `MemoryError`, `ConnectionError` | Retry, circuit breaker, degrade |

### Result Pattern (Alternative to Exceptions)
```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E", bound=Exception)

@dataclass(frozen=True)
class Result(Generic[T, E]):
    value: T | None = None
    error: E | None = None
    
    @property
    def is_ok(self) -> bool:
        return self.error is None
    
    @property
    def is_err(self) -> bool:
        return self.error is not None
    
    def unwrap(self) -> T:
        if self.error:
            raise self.error
        return self.value
    
    def map[U](self, func: Callable[[T], U]) -> "Result[U, E]":
        if self.error:
            return Result(error=self.error)
        try:
            return Result(value=func(self.value))
        except Exception as e:
            return Result(error=e)

# Usage
def parse_int(s: str) -> Result[int, ValueError]:
    try:
        return Result(value=int(s))
    except ValueError as e:
        return Result(error=e)

result = parse_int("42")
if result.is_ok:
    print(result.value)
else:
    print(f"Error: {result.error}")
```

---

## Decision Rules

| Situation | Pattern |
|-----------|---------|
| Expected failure (validation, not found) | Custom exception or `Result` |
| Programming bug | `assert` or let built-in raise |
| External API failure | Custom exception wrapping original |
| Retryable failure | Catch specific, retry with backoff |
| Cleanup needed | `try/finally` or context manager |
| Multiple independent failures | `ExceptionGroup` (3.11+) |

---

## Preferred Patterns

```python
# Validation at boundaries
def create_user(data: dict) -> User:
    # Validate input early
    email = data.get("email")
    if not email or "@" not in email:
        raise ValidationError("email", "Invalid email format")
    
    # Business logic
    if user_repo.exists(email):
        raise ConflictError("User already exists")
    
    return user_repo.save(User(email=email))

# Graceful degradation
async def get_user_profile(user_id: str) -> UserProfile:
    try:
        return await user_service.get_profile(user_id)
    except UserService.Unavailable:
        # Fallback to cache
        return await cache.get_profile(user_id)
    except UserService.NotFound:
        raise NotFoundError("User", user_id)

# Structured error responses (API)
def handle_error(e: Exception) -> ErrorResponse:
    if isinstance(e, ValidationError):
        return ErrorResponse(400, e.code, e.details)
    if isinstance(e, NotFoundError):
        return ErrorResponse(404, e.code, e.details)
    if isinstance(e, ConflictError):
        return ErrorResponse(409, e.code, e.details)
    logger.exception("Unhandled error")
    return ErrorResponse(500, "INTERNAL_ERROR", {})
```

---

## Avoid

- Bare `except:` or `except Exception:`
- Swallowing exceptions silently
- Using exceptions for control flow (except EAFP)
- Custom exceptions without `__init__` for context
- Raising generic `Exception` or `RuntimeError`
- Losing original exception context (use `from e`)
- Catching `KeyboardInterrupt` / `SystemExit` (unless shutting down)

---

## Change Scope

- Prefer the smallest correct change to error handling
- Preserve existing public exception interfaces unless task requires otherwise
- Do not refactor unrelated error handling code
- Avoid adding new exception classes when existing ones suffice
- Preserve existing error messages unless they leak secrets

---

## Verification

- Test error paths explicitly (not just happy path)
- Verify exception messages don't leak secrets or internal details
- Check logging includes context for debugging (extra fields, exception chain)
- Ensure `Result` pattern doesn't hide errors silently
- Run `bandit -r src/` and check for exception-related warnings

---

## Related Skills

- `generation/workflow.md`
- `generation/async_concurrency.md` (async errors)
- `security/input_validation.md`
- `testing/edge_cases.md`
- `quality/functions.md`