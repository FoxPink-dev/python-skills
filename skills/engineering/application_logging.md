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

### Context Injection (Correlation IDs)
```python
import contextvars
import uuid

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)
user_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)

class CorrelationFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        record.user_id = user_id_var.get()
        return True

# In middleware (ASGI/WSGI)
async def correlation_middleware(request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_var.set(request_id)
    if hasattr(request, "user") and request.user:
        user_id_var.set(str(request.user.id))
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        request_id_var.set(None)
        user_id_var.set(None)

# Usage - all logs in this request include correlation IDs
log.info("processing")  # Includes request_id, user_id
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

### Log Sanitization (Prevent Secret/PII Leakage)
```python
import re
from urllib.parse import urlparse, urlunparse

# Patterns that indicate sensitive data
SENSITIVE_PATTERNS = [
    (re.compile(r'(?i)(password|secret|token|key|api_key|apikey|auth|credential)\s*[:=]\s*\S+'), r'\1=***'),
    (re.compile(r'(?i)bearer\s+\S+'), 'Bearer ***'),
    (re.compile(r'(?i)authorization\s*:\s*\S+'), 'Authorization: ***'),
    (re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'), '****-****-****-****'),  # Credit card
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '***-**-****'),  # SSN
]

def sanitize_log_message(message: str) -> str:
    """Remove sensitive data from log messages."""
    for pattern, replacement in SENSITIVE_PATTERNS:
        message = pattern.sub(replacement, message)
    return message

def sanitize_url(url: str) -> str:
    """Remove credentials from URLs."""
    try:
        parsed = urlparse(url)
        if parsed.password:
            netloc = f"{parsed.username}:***@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            return urlunparse(parsed._replace(netloc=netloc))
    except Exception:
        pass
    return url

class SanitizingFilter(logging.Filter):
    """Filter that sanitizes log records before emission."""
    def filter(self, record: logging.LogRecord) -> bool:
        # Sanitize message
        if isinstance(record.msg, str):
            record.msg = sanitize_log_message(record.msg)
        # Sanitize args
        if record.args:
            record.args = tuple(
                sanitize_log_message(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )
        # Sanitize extra fields
        for key, value in record.__dict__.items():
            if key not in {"name", "msg", "args", "created", "filename", "funcName",
                          "levelname", "levelno", "lineno", "module", "msecs",
                          "message", "name", "pathname", "process", "processName",
                          "relativeCreated", "thread", "threadName", "exc_info",
                          "exc_text", "stack_info", "getMessage"}:
                if isinstance(value, str):
                    record.__dict__[key] = sanitize_log_message(value)
        return True

# Usage
handler = logging.StreamHandler()
handler.addFilter(SanitizingFilter())
handler.addFilter(CorrelationFilter())  # Also add correlation
```

### Production Gotchas

| Gotcha | Symptom | Fix |
|--------|---------|-----|
| Secrets in logs | Credentials leaked in log aggregation | Add `SanitizingFilter` to all handlers |
| PII in logs | GDPR violation | Sanitize email, IP, names in `extra` |
| No correlation IDs | Can't trace request across services | Add `CorrelationFilter` in middleware |
| Blocking logging | High latency under load | Use `QueueHandler` + `QueueListener` |
| Missing log rotation | Disk full | Use `RotatingFileHandler` or external |
| DEBUG in production | Performance, noise | Set root level to INFO, per-module DEBUG |

### High-Volume Logging (Non-Blocking)
```python
import logging
import logging.handlers
import queue

# Queue-based handler for high throughput
log_queue: queue.Queue = queue.Queue(-1)
queue_handler = logging.handlers.QueueHandler(log_queue)
root = logging.getLogger()
root.addHandler(queue_handler)

# Listener runs in separate thread
listener = logging.handlers.QueueListener(
    log_queue,
    logging.StreamHandler(),  # Or file handler
    respect_handler_level=True,
)
listener.start()

# On shutdown
listener.stop()
```

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