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

## Related Skills

- `engineering/configuration.md`
- `security/secrets.md`
- `stdlib/os_sys.md` (environment config)
- `generation/error_handling.md` (exception logging)