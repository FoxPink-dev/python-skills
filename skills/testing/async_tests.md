---
name: testing_async_tests
purpose: Testing async code with pytest-asyncio
category: testing
triggers:
  - async
  - pytest-asyncio
  - asyncio
  - async test
  - async fixture
  - async mock
dependencies:
  - generation/async_concurrency.md
  - testing/organization.md
  - testing/fixtures_mocks.md
  - testing/edge_cases.md
priority: supporting
estimated_tokens: 2300
---
# Testing: Async Tests

**Purpose**: Testing async code with pytest-asyncio.

**When to use**: Any async functions, services, or integrations.

---

## Core Rules

### Setup
```ini
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Basic Async Test
```python
import pytest
import pytest_asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == "expected"
```

### Async Fixtures
```python
# conftest.py
import pytest_asyncio

@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    client = AsyncClient()
    yield client
    await client.aclose()

@pytest_asyncio.fixture
async def db_pool() -> asyncpg.Pool:
    pool = await asyncpg.create_pool("postgresql://test:test@localhost/test")
    yield pool
    await pool.close()
```

### Async Mocking
```python
from unittest.mock import AsyncMock

@pytest.fixture
def mock_async_service():
    service = AsyncMock()
    service.fetch.return_value = {"data": "test"}
    service.fetch.side_effect = [
        {"data": "first"},
        {"data": "second"},
        Exception("error"),
    ]
    return service

@pytest.mark.asyncio
async def test_async_mock(mock_async_service):
    result = await mock_async_service.fetch()
    assert result == {"data": "first"}
    mock_async_service.fetch.assert_awaited_once()
```

### Testing Async Generators
```python
@pytest.mark.asyncio
async def test_async_generator():
    results = []
    async for item in async_generator():
        results.append(item)
    assert results == [1, 2, 3]

# Or collect
@pytest.mark.asyncio
async def test_async_generator_collect():
    items = [item async for item in async_generator()]
    assert items == [1, 2, 3]
```

### Testing Timeouts
```python
import asyncio

@pytest.mark.asyncio
async def test_timeout():
    async def slow():
        await asyncio.sleep(10)
        return "done"
    
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow(), timeout=0.1)
```

### Testing Concurrency
```python
@pytest.mark.asyncio
async def test_concurrent_requests():
    async def fetch(url):
        await asyncio.sleep(0.1)
        return url
    
    urls = [f"http://example.com/{i}" for i in range(10)]
    results = await asyncio.gather(*[fetch(u) for u in urls])
    assert len(results) == 10

# With semaphore
@pytest.mark.asyncio
async def test_rate_limited():
    sem = asyncio.Semaphore(2)
    
    async def limited_fetch(url):
        async with sem:
            await asyncio.sleep(0.1)
            return url
    
    # Should take ~0.5s (10 tasks / 2 concurrent * 0.1s)
    import time
    start = time.monotonic()
    await asyncio.gather(*[limited_fetch(f"url{i}") for i in range(10)])
    elapsed = time.monotonic() - start
    assert 0.4 < elapsed < 0.7
```

### Testing Cancellation
```python
@pytest.mark.asyncio
async def test_cancellation():
    async def long_running():
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            # Cleanup
            raise
    
    task = asyncio.create_task(long_running())
    await asyncio.sleep(0.01)
    task.cancel()
    
    with pytest.raises(asyncio.CancelledError):
        await task
```

### TaskGroup (Python 3.11+)
```python
@pytest.mark.asyncio
async def test_task_group():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch("url1"))
        task2 = tg.create_task(fetch("url2"))
    
    # All completed or exception raised
    assert task1.result() == "url1"
    assert task2.result() == "url2"
```

---

## Decision Rules

| Need | Pattern |
|------|---------|
| Async function | `@pytest.mark.asyncio` |
| Async fixture | `@pytest_asyncio.fixture` |
| External async service | `AsyncMock` |
| Timeout behavior | `asyncio.wait_for` |
| Cancellation | `task.cancel()` + `CancelledError` |
| Concurrent behavior | `asyncio.gather` / `TaskGroup` |

---

## Preferred Patterns

```python
# Test with real async dependencies (integration)
@pytest.mark.asyncio
async def test_database_integration(db_pool):
    async with db_pool.acquire() as conn:
        await conn.execute("INSERT INTO test (value) VALUES ($1)", "test")
        row = await conn.fetchrow("SELECT value FROM test WHERE value = $1", "test")
        assert row["value"] == "test"

# Test retry logic
@pytest.mark.asyncio
async def test_retry_on_failure():
    call_count = 0
    
    async def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("fail")
        return "success"
    
    result = await retry_async(flaky, attempts=3, base_delay=0.01)
    assert result == "success"
    assert call_count == 3
```

---

## Avoid

- Sync tests for async code
- `asyncio.run()` in tests (use pytest-asyncio)
- Blocking sleeps (`time.sleep`) in async tests
- Not awaiting mocks (`assert_awaited` vs `assert_called`)
- Shared event loop state between tests

---

## Validation Considerations

- `pytest-asyncio` handles event loop per test
- No "Event loop is closed" errors
- Timeout tests actually timeout (not hang)
- Cancellation cleanup verified

---

## Related Skills

- `generation/async_concurrency.md`
- `testing/organization.md`
- `testing/fixtures_mocks.md`
- `testing/edge_cases.md`