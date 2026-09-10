---
name: logging
purpose: Structured application logging.
category: stdlib
triggers:
  - logging
  - logger
  - handler
  - formatter
  - level
  - config
dependencies: []
related: []
priority: supporting
estimated_tokens: 1149
---
# Stdlib: logging

**Purpose**: Structured application logging.

**When to use**: All application logging. Never `print()` in production code.

---

## Core Rules

### Basic Setup
```python
import logging

# Module-level logger (standard pattern)
logger = logging.getLogger(__name__)

# Logging levels
logger.debug("Detailed diagnostic")
logger.info("General operation")
logger.warning("Unexpected, but handled")
logger.error("Function failed")
logger.critical("System may fail")

# With context
logger.info("User login", extra={"user_id": 123, "ip": "1.2.3.4"})
```

### Configuration (Application Entry Point)
```python
import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": "app.log",
            "maxBytes": 10_000_000,
            "backupCount": 5,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
    "loggers": {
        "myapp": {"level": "DEBUG", "propagate": True},
        "httpx": {"level": "WARNING"},  # Quiet noisy libs
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Structured Logging (Recommended)
```python
# Use extra for structured data
logger.info("Order processed", extra={
    "order_id": "ORD-123",
    "amount": 99.99,
    "currency": "USD",
    "customer_id": "CUST-456",
})

# Or use a structured logging library (structlog)
import structlog

log = structlog.get_logger()
log.info("order_processed", order_id="ORD-123", amount=99.99)
```

### Correlation IDs (Request Tracing)
```python
import contextvars
import logging

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)

class CorrelationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True

# In middleware
request_id_var.set("req-123")
logger.info("processing")  # Includes request_id in log record

# Formatter includes request_id
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s [%(request_id)s]: %(message)s"
)
```

### Log Sanitization (Prevent Secret/PII Leakage)
```python
import re
from urllib.parse import urlparse, urlunparse

SENSITIVE_PATTERNS = [
    (re.compile(r'(?i)(password|secret|token|key|api_key|apikey|auth|credential)\s*[:=]\s*\S+'), r'\1=***'),
    (re.compile(r'(?i)bearer\s+\S+'), 'Bearer ***'),
    (re.compile(r'(?i)authorization\s*:\s*\S+'), 'Authorization: ***'),
]

def sanitize_log_message(message: str) -> str:
    for pattern, replacement in SENSITIVE_PATTERNS:
        message = pattern.sub(replacement, message)
    return message

class SanitizingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = sanitize_log_message(record.msg)
        if record.args:
            record.args = tuple(
                sanitize_log_message(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )
        return True

# Usage
handler = logging.StreamHandler()
handler.addFilter(SanitizingFilter())
handler.addFilter(CorrelationFilter())
```

### Exception Logging
```python
try:
    risky()
except Exception:
    logger.exception("Operation failed")  # Includes traceback
    # Or:
    logger.error("Operation failed", exc_info=True)
```

### Lazy Evaluation (Performance)
```python
# Arguments evaluated only if level enabled
logger.debug("Expensive: %s", expensive_computation)  # Not f-string!

# For complex objects
logger.debug("Data: %s", lambda: repr(large_object))
```

---

## Decision Rules

| Situation | Approach |
|-----------|----------|
| Application code | `logger = logging.getLogger(__name__)` |
| Library code | Same, but don't configure — let app configure |
| Structured data | `extra={...}` or `structlog` |
| Exceptions | `logger.exception()` or `exc_info=True` |
| High-volume debug | Lazy `%s` formatting |
| Production | JSON format, file rotation |
| Development | Human-readable, console |

---

## Preferred Patterns

```python
# Library: just get logger, don't configure
# mylib/__init__.py
import logging
log = logging.getLogger(__name__)

# Application: configure once at startup
# main.py
def setup_logging(level: str = "INFO", json_format: bool = False):
    import logging.config
    # ... dictConfig as above

# Context injection (middleware, decorators)
def with_context(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        old_factory = logging.getLogRecordFactory()
        def factory(*a, **kw):
            record = old_factory(*a, **kw)
            record.request_id = getattr(request_context, "id", None)
            return record
        logging.setLogRecordFactory(factory)
        try:
            return func(*args, **kwargs)
        finally:
            logging.setLogRecordFactory(old_factory)
    return wrapper
```

---

## Avoid

- `print()` in production code
- `logging.basicConfig()` in libraries (configures root globally)
- `logging.getLogger()` without name (root logger)
- f-strings in logging calls (evaluates always)
- Logging sensitive data (secrets, PII, tokens)
- Excessive DEBUG in production
- Catching and logging then re-raising without context

---

## Validation Considerations

- Test log output format
- Verify log levels in different environments
- Check log rotation works
- Ensure no PII in logs (automated scanning)

---

## Gotchas

### f-strings in Logging Evaluate Always
```python
# BAD — f-string evaluates even if DEBUG disabled
logger.debug(f"Processing {expensive_computation()}")

# GOOD — %s lazy evaluation (only evaluates if level enabled)
logger.debug("Processing %s", expensive_computation())
```
**Rule**: Use `%s` formatting in logging calls, not f-strings. The `%s` form defers evaluation until the message is actually emitted.

### `logging.basicConfig()` Configures Root Globally
```python
# In library code — BAD
logging.basicConfig(level=logging.DEBUG)  # Overrides app config!

# In library code — GOOD
logger = logging.getLogger(__name__)  # Just get logger, let app configure
```
**Rule**: Libraries should only call `getLogger(__name__)`. Never call `basicConfig()` in library code — itconfigures the root logger and breaks application logging setup.

### Mutable Default in Logger Extra
```python
# BAD — shared dict across calls
def log_action(action, extra={}):
    extra["action"] = action
    logger.info("Action", extra=extra)

# GOOD
def log_action(action, extra=None):
    if extra is None:
        extra = {}
    extra["action"] = action
    logger.info("Action", extra=extra)
```
**Rule**: The `extra` dict in logging calls should not use mutable defaults.

### `disable_existing_loggers` Default
```python
# dictConfig default: disable_existing_loggers=True
# This disables ALL loggers except root — surprises in libraries

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # Keep existing loggers
    ...
}
```
**Rule**: Set `disable_existing_loggers: False` in dictConfig unless you explicitly want to suppress library loggers.

### Exception Logging with `logger.exception()` vs `logger.error(exc_info=True)`
```python
# These are equivalent:
logger.exception("Failed")  # Includes traceback, sets exc_info=True automatically
logger.error("Failed", exc_info=True)  # Same behavior

# But logger.exception() ALWAYS includes traceback
# Use logger.error() when you want conditional traceback
```
**Rule**: `logger.exception()` is shorthand for `logger.error(..., exc_info=True)`. Use it in except blocks.

---

## Related Skills

- `engineering/configuration.md`
- `security/secrets.md`
- `stdlib/os_sys.md` (environment config)
- `generation/error_handling.md` (exception logging)