---
name: generation_async_concurrency
purpose: Async/await patterns, concurrency primitives, and correct usage
category: generation
triggers:
  - async
  - await
  - concurrent
  - parallel
  - asyncio
  - task
  - semaphore
  - queue
dependencies:
  - generation/error_handling.md
  - testing/async_tests.md
  - stdlib/subprocess.md
  - engineering/http_clients.md
priority: primary
estimated_tokens: 2700
---
# Generation: Async and Concurrency

**Purpose**: Async/await patterns, concurrency primitives, and correct usage.

**When to use**: I/O-bound operations, high-concurrency servers, parallel I/O.

---

## Core Rules

### When to Use Async
- I/O-bound: HTTP requests, database, file I/O, subprocess
- Many concurrent connections (web servers, websockets)
- Not for CPU-bound (use multiprocessing)

### Basic Syntax
```python
import asyncio

async def fetch(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()

async def main():
    result = await fetch("https://example.com")
    print(result)

asyncio.run(main())
```

### Task Management
```python
async def main():
    # Concurrent execution
    task1 = asyncio.create_task(fetch(url1))
    task2 = asyncio.create_task(fetch(url2))
    result1, result2 = await asyncio.gather(task1, task2)
    
    # With timeout
    try:
        result = await asyncio.wait_for(fetch(url), timeout=5.0)
    except asyncio.TimeoutError:
        ...
    
    # As completed
    for coro in asyncio.as_completed([fetch(u) for u in urls]):
        result = await coro
        process(result)
    
    # Shield from cancellation
    await asyncio.shield(critical_operation())
```

### Cancellation
```python
async def long_running():
    try:
        while True:
            await asyncio.sleep(1)
            # Check cancellation
    except asyncio.CancelledError:
        cleanup()
        raise  # Must re-raise!

# Cancellation propagation
async def parent():
    child = asyncio.create_task(long_running())
    await asyncio.sleep(0.1)
    child.cancel()
    try:
        await child
    except asyncio.CancelledError:
        pass
```

### Async Context Managers
```python
class AsyncResource:
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return False  # Don't suppress

async def use():
    async with AsyncResource() as r:
        await r.do_something()
```

### Async Iterators
```python
async def async_gen() -> AsyncGenerator[int, None]:
    for i in range(10):
        await asyncio.sleep(0.1)
        yield i

async def consume():
    async for item in async_gen():
        print(item)
    
    # Or collect
    items = [item async for item in async_gen()]
```

### Synchronization Primitives
```python
# Lock
lock = asyncio.Lock()
async with lock:
    critical_section()

# Semaphore (limit concurrency)
sem = asyncio.Semaphore(10)
async with sem:
    await limited_operation()

# Event
event = asyncio.Event()
async def waiter():
    await event.wait()
async def setter():
    await asyncio.sleep(1)
    event.set()

# Queue
queue: asyncio.Queue[str] = asyncio.Queue()
await queue.put("item")
item = await queue.get()

# Condition
cond = asyncio.Condition()
async with cond:
    await cond.wait()
    cond.notify()
```

### Running in Threads (Blocking I/O)
```python
# Run sync function in thread pool
result = await asyncio.to_thread(blocking_func, arg1, arg2)

# Custom executor
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, blocking_func, arg1)
```

### Exception Handling
```python
async def main():
    try:
        await risky_async()
    except SpecificError:
        handle()
    except ExceptionGroup as eg:  # Python 3.11+
        for e in eg.exceptions:
            handle(e)
    except* ValueError as eg:  # except* syntax (3.11+)
        for e in eg.exceptions:
            handle(e)
    finally:
        cleanup()
```

### Task Groups (Python 3.11+)
```python
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(fetch(url1))
        task2 = tg.create_task(fetch(url2))
    # All tasks completed or first exception raised
    results = [task1.result(), task2.result()]
```

---

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| CPU-bound work | GIL prevents parallelism | Use `multiprocessing` |
| Simple scripts | Overhead without benefit | Use synchronous code |
| Blocking I/O in async | Defeats purpose | Use `asyncio.to_thread` |
| `asyncio.run()` inside async | Nested event loops | Use `asyncio.create_task` |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Blocking call in async | Event loop blocked | Use `asyncio.to_thread` |
| Not tracking tasks | Memory leaks | Store task references |
| Catching `CancelledError` without re-raise | Broken cancellation | Always re-raise |
| `asyncio.run()` inside async | Nested event loops | Use `asyncio.create_task` |
| Mixing `asyncio` with `threading` | Deadlocks, race conditions | Use `asyncio` primitives |

### Anti-Pattern

```python
# NEVER: Blocking call in async
async def fetch():
    import requests
    return requests.get(url)  # Blocks event loop!

# NEVER: asyncio.run() inside async
async def main():
    await asyncio.run(other())  # Nested event loops!

# BETTER: Use async libraries
async def fetch():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()
```

| Situation | Pattern |
|-----------|---------|
| Multiple independent I/O | `asyncio.gather` / `TaskGroup` |
| Rate limiting | `Semaphore` |
| Producer/consumer | `asyncio.Queue` |
| Timeout | `asyncio.wait_for` |
| Cancellation | `task.cancel()` + `CancelledError` handling |
| Blocking call | `asyncio.to_thread` |
| Background task | `create_task` (track for cleanup) |
| Cleanup on exit | `async with` / `try/finally` |

---

## Preferred Patterns

```python
# Bounded concurrency
async def fetch_all(urls: list[str], max_concurrent: int = 10) -> list[str]:
    sem = asyncio.Semaphore(max_concurrent)
    
    async def bounded_fetch(url: str) -> str:
        async with sem:
            return await fetch(url)
    
    return await asyncio.gather(*[bounded_fetch(u) for u in urls])

# Retry with backoff
async def retry_async(
    func: Callable[..., Awaitable[T]],
    *args,
    attempts: int = 3,
    base_delay: float = 1.0,
    **kwargs,
) -> T:
    for attempt in range(attempts):
        try:
            return await func(*args, **kwargs)
        except Exception:
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(base_delay * (2 ** attempt))

# Graceful shutdown
async def run_server():
    server = await start_server()
    try:
        await server.serve_forever()
    except asyncio.CancelledError:
        await server.shutdown()
        raise
```

---

## Avoid

- `asyncio.run()` inside async function (nested event loops)
- Blocking calls in async functions (use `to_thread`)
- Creating tasks without tracking (memory leaks)
- Catching `CancelledError` without re-raising
- Mixing `asyncio` with `threading` primitives
- Global event loop references

---

## Python Version Notes

- 3.11+: `TaskGroup`, `except*`, `asyncio.timeout()`
- 3.10+: `asyncio.timeout()` context manager
- 3.7+: `asyncio.run()`, `asyncio.create_task()`

---

## Validation Considerations

- Test cancellation scenarios
- Test timeout behavior
- Check for resource leaks (open connections, files)
- Verify no blocking calls in async path
- `pytest-asyncio` for testing

---

## Related Skills

- `generation/error_handling.md`
- `testing/async_tests.md`
- `stdlib/subprocess.md` (async subprocess)
- `engineering/http_clients.md` (aiohttp, httpx)