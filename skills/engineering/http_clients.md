---
name: engineering_http_clients
purpose: HTTP client selection and usage patterns
category: engineering
triggers:
  - http
  - request
  - client
  - api
  - rest
  - webhook
  - download
dependencies:
  - generation/async_concurrency.md
  - generation/error_handling.md
  - engineering/configuration.md
  - security/secrets.md
  - testing/organization.md
priority: primary
estimated_tokens: 2500
---
# Engineering: HTTP Clients

**Purpose**: HTTP client selection and usage patterns.

**When to use**: Making HTTP requests (APIs, webhooks, downloads).

---

## Core Rules

### Client Selection

| Need | Client |
|------|--------|
| Sync, simple | `requests` |
| Sync + HTTP/2 | `httpx` (sync) |
| Async | `httpx` / `aiohttp` |
| Stdlib only | `urllib.request` (avoid) |
| Testing | `respx` / `pytest-httpx` / `requests-mock` |

### httpx (Recommended — Sync + Async)
```python
import httpx

# Sync
client = httpx.Client(timeout=30.0, limits=httpx.Limits(max_connections=100))
response = client.get("https://api.example.com/users")
client.close()

# Context manager
with httpx.Client() as client:
    response = client.get(url)

# Async
async with httpx.AsyncClient() as client:
    response = await client.get(url)

# Common options
client = httpx.Client(
    base_url="https://api.example.com",
    headers={"User-Agent": "MyApp/1.0"},
    timeout=httpx.Timeout(connect=5.0, read=30.0),
    follow_redirects=True,
    limits=httpx.Limits(max_keepalive_connections=20),
)
```

### Response Handling
```python
response = client.get(url)

# Status
response.status_code
response.is_success
response.raise_for_status()  # Raises HTTPStatusError

# Content
response.text          # str (decoded)
response.content       # bytes
response.json()        # Parsed JSON
response.iter_bytes()  # Stream

# Headers
response.headers["Content-Type"]
response.headers.get("X-Custom")
```

### Error Handling
```python
import httpx

try:
    response = client.get(url, timeout=10.0)
    response.raise_for_status()
except httpx.TimeoutException:
    logger.warning("Request timed out")
    raise ServiceTimeout()
except httpx.ConnectError:
    logger.warning("Connection failed")
    raise ServiceUnavailable()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        raise NotFoundError()
    elif e.response.status_code == 429:
        raise RateLimited(retry_after=e.response.headers.get("Retry-After"))
    else:
        logger.error("HTTP error", status=e.response.status_code)
        raise ServiceError()
```

### Retry Logic
```python
from httpx import Retry
from httpx._transports.default import RetryStrategy

# Built-in retry (httpx 0.25+)
transport = httpx.HTTPTransport(
    retries=Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
)
client = httpx.Client(transport=transport)

# Or use tenacity for complex retry
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(httpx.RequestError),
)
async def fetch_with_retry(client: httpx.AsyncClient, url: str) -> httpx.Response:
    return await client.get(url)
```

### Authentication
```python
# Bearer token
headers = {"Authorization": f"Bearer {token}"}

# Basic auth
auth = httpx.BasicAuth("user", "pass")

# Custom auth
class APIKeyAuth(httpx.Auth):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def auth_flow(self, request):
        request.headers["X-API-Key"] = self.api_key
        yield request

client = httpx.Client(auth=APIKeyAuth("key"))
```

### Streaming Large Responses
```python
# Download large file
with client.stream("GET", url) as response:
    response.raise_for_status()
    with Path("large_file").open("wb") as f:
        for chunk in response.iter_bytes(chunk_size=8192):
            f.write(chunk)

# Async streaming
async with client.stream("GET", url) as response:
    async for chunk in response.aiter_bytes():
        process(chunk)
```

### Testing
```python
import pytest
import respx
import httpx

@respx.mock
async def test_api():
    respx.get("https://api.example.com/users").mock(
        return_value=httpx.Response(200, json=[{"id": 1}])
    )
    
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.example.com/users")
        assert resp.json() == [{"id": 1}]
```

---

## Decision Rules

| Situation | Pattern |
|-----------|---------|
| Simple sync requests | `httpx.Client()` |
| High concurrency sync | `httpx.Client` with limits |
| Async application | `httpx.AsyncClient` |
| Complex retry/backoff | `tenacity` + `httpx` |
| WebSocket | `httpx` (experimental) or `websockets` |
| Testing | `respx` (async) or `requests-mock` (sync) |

---

## Preferred Patterns

```python
# Reusable client factory
def create_client(
    base_url: str,
    timeout: float = 30.0,
    api_key: str | None = None,
) -> httpx.Client:
    headers = {"User-Agent": "MyApp/1.0"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    return httpx.Client(
        base_url=base_url,
        headers=headers,
        timeout=httpx.Timeout(timeout),
        limits=httpx.Limits(max_connections=50),
    )

# Service wrapper
class APIService:
    def __init__(self, client: httpx.Client):
        self.client = client
    
    def get_user(self, user_id: str) -> User:
        resp = self.client.get(f"/users/{user_id}")
        resp.raise_for_status()
        return User.model_validate(resp.json())
```

---

## Avoid

- Creating new client per request (no connection pooling)
- No timeout (hangs forever)
- Ignoring `raise_for_status()`
- Blocking sync client in async code
- Logging full response bodies (may contain secrets)
- Hardcoding URLs (use config + base_url)

---

## Validation Considerations

- Test timeout behavior
- Test retry logic
- Test auth handling
- Mock external APIs in tests
- Check connection pooling works

---

## Related Skills

- `generation/async_concurrency.md`
- `generation/error_handling.md`
- `engineering/configuration.md`
- `security/secrets.md`
- `testing/organization.md`