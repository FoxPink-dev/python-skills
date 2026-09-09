# Quality: Documentation

**Purpose**: Document public APIs and non-obvious behavior appropriately.

**When to use**: Public modules, classes, functions, complex systems.

---

## Core Rules

### Documentation Levels

| Level | Audience | Format |
|-------|----------|--------|
| **Docstrings** | Developers using API | In-code, accessible via `help()` |
| **README** | Users, contributors | Markdown in repo root |
| **Architecture docs** | Maintainers | Project-specific (e.g., `project-docs/architecture.md`) |
| **API reference** | External consumers | Generated (Sphinx, pdoc) |
| **Changelog** | Users | `CHANGELOG.md` |

### Docstring Format (Google/NumPy/Sphinx)
```python
def fetch_users(
    client: APIClient,
    filters: UserFilters | None = None,
    limit: int = 100,
) -> list[User]:
    """Fetch users matching filters.
    
    Args:
        client: Authenticated API client.
        filters: Optional filters (name, status, role).
        limit: Maximum results (default 100, max 1000).
        
    Returns:
        List of users matching criteria.
        
    Raises:
        APIError: If request fails.
        ValidationError: If limit exceeds maximum.
        
    Example:
        >>> client = APIClient(token="abc")
        >>> users = fetch_users(client, UserFilters(active=True), limit=50)
    """
    ...
```

### Module Docstring
```python
"""Payment processing module.

Provides payment authorization, capture, and refund operations.
Supports multiple gateways via the PaymentGateway protocol.

Typical usage:
    gateway = StripeGateway(api_key="sk_...")
    processor = PaymentProcessor(gateway)
    result = processor.charge(amount=1000, currency="USD")
"""
```

### Class Docstring
```python
class PaymentProcessor:
    """Orchestrates payment operations across gateways.
    
    Handles retry logic, idempotency, and gateway failover.
    Not thread-safe; use one instance per request.
    
    Attributes:
        gateway: Primary payment gateway.
        fallback: Optional fallback gateway.
    """
    
    def __init__(self, gateway: PaymentGateway, fallback: PaymentGateway | None = None):
        self.gateway = gateway
        self.fallback = fallback
```

---

## Decision Rules

| Element | Docstring Required? |
|---------|---------------------|
| Public module | Yes |
| Public class | Yes |
| Public function/method | Yes |
| Private (`_` prefix) | Optional |
| Override (same behavior) | No (inherit) |
| Property | Yes (describe what it returns) |

### README Structure
```markdown
# Package Name

One-line description.

## Installation
```bash
pip install package-name
```

## Quick Start
```python
from package import main
main()
```

## Configuration
Environment variables...

## API Reference
Link to generated docs.

## Contributing
...

## License
...
```

---

## Preferred Patterns

```python
# Type hints + docstring = complete API docs
def process(
    data: InputData,
    config: ProcessingConfig = ProcessingConfig(),
) -> OutputData:
    """Process input data according to configuration.
    
    Args:
        data: Input to process. Must be validated.
        config: Processing options. Defaults used if omitted.
        
    Returns:
        Processed output data.
        
    Raises:
        ValidationError: If input data is invalid.
        ProcessingError: If processing fails.
    """
    ...
```

---

## Avoid

- Missing docstrings on public API
- Docstrings that just repeat signature
- Outdated docstrings (update with code)
- Documenting private implementation details
- Redundant type information in docstring (use type hints)

---

## Validation Considerations

- `pydocstyle` / `ruff` docstring checks
- `interrogate` for coverage
- `pdoc` / `sphinx` build succeeds
- Examples in docstrings runnable (doctest)

---

## Related Skills

- `quality/comments.md`
- `generation/type_hints.md`
- `engineering/packaging.md`
- `quality/readability.md`