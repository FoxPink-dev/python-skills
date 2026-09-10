---
name: application_logging
purpose: Application-level logging setup and patterns.
category: engineering
triggers:
  - logging
  - logger
  - loguru
  - structlog
  - structured-logging
dependencies: []
related: []
priority: primary
estimated_tokens: 1356
---
# Engineering: Logging (Application)

**Purpose**: Application-level logging setup and patterns.

**When to use**: Setting up logging for applications (not libraries).

---

## Core Rules

### Application vs Library Logging
- **Application**: Configures logging (handlers, formatters, levels)
- **Library**: Only uses `logging.getLogger(__name__)`, adds `NullHandler`

### Structured Logging (JSON)
```python
import logging
import json
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {"name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "msecs",
                          "message", "name", "pathname", "process", "processName",
                          "relativeCreated", "thread", "threadName", "exc_info",
                          "exc_text", "stack_info", "getMessage"}:
                log_data[key] = value
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, default=str)

# Setup
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
root = logging.getLogger()
root.addHandler(handler)
root.setLevel(logging.INFO)
```

### Structlog (Better Structured Logging)
```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if dev else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()

# Usage
log.info("user_login", user_id=123, ip="1.2.3.4")
log.error("db_failed", error=str(e), query="SELECT ...")
```

### Context Injection
```python
import contextvars

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)

class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True

# In middleware
request_id_var.set("req-123")
log.info("processing")  # Includes request_id
```

### Log Levels Guide
| Level | Use Case |
|-------|----------|
| DEBUG | Detailed diagnostic (dev only) |
| INFO | General operations (requests, startup) |
| WARNING | Unexpected but handled (retry, fallback) |
| ERROR | Operation failed (5xx, failed request) |
| CRITICAL | System may stop (OOM, disk full) |

---

## Decision Rules

| Situation | Setup |
|-----------|-------|
| Simple app | `logging.basicConfig` + JSON formatter |
| Production service | structlog + JSON + log aggregation |
| Library | `getLogger(__name__)` + `NullHandler` |
| CLI tool | Rich handler for pretty output |

---

## Preferred Patterns

```python
# Centralized setup (call once at startup)
def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    dev_mode: bool = False,
) -> None:
    import logging
    import sys
    
    # Clear existing
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)
    
    handler = logging.StreamHandler(sys.stdout)
    
    if json_format and not dev_mode:
        handler.setFormatter(JSONFormatter())
    elif dev_mode:
        import rich.logging
        handler = rich.logging.RichHandler(rich_tracebacks=True)
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
    
    root.addHandler(handler)
    root.setLevel(level)
    
    # Quiet noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

# Usage in app
log = logging.getLogger(__name__)

def process_order(order_id: str):
    log.info("order_started", order_id=order_id)
    try:
        do_work()
        log.info("order_completed", order_id=order_id)
    except Exception as e:
        log.exception("order_failed", order_id=order_id, error=str(e))
        raise
```

---

## Avoid

- `print()` in production code
- Logging sensitive data (passwords, tokens, PII)
- Excessive DEBUG in production
- No log rotation (use `RotatingFileHandler` or external)
- Blocking I/O in logging (use `QueueHandler` + `QueueListener` for high volume)

---

## Validation Considerations

- Test log output format
- Verify log levels in different environments
- Check structured fields are present
- Ensure no PII in logs
- Test high-volume logging doesn't block

---

## Related Skills

- `stdlib/logging.md`
- `engineering/configuration.md`
- `security/secrets.md`
- `generation/error_handling.md`