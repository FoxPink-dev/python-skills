---
name: database
purpose: Database access patterns and best practices
category: engineering
triggers:
  - database
  - sql
  - query
  - orm
  - sqlite
  - postgresql
  - mysql
  - migration
dependencies:
  - engineering/configuration
  - generation/async_concurrency
  - generation/error_handling
  - testing/organization
related:
  - security/sql_injection
  - security/input_validation
  - generation/async_concurrency
  - testing/regression_tests
priority: primary
estimated_tokens: 2200
---
# Engineering: Database

**Purpose**: Database access patterns and best practices.

**When to use**: Any code interacting with databases.

---

## Core Rules

### Driver Selection
| Database | Async Driver | Sync Driver |
|----------|--------------|-------------|
| PostgreSQL | `asyncpg` | `psycopg` (v3) |
| MySQL | `aiomysql` | `pymysql` |
| SQLite | `aiosqlite` | `sqlite3` (stdlib) |
| MongoDB | `motor` | `pymongo` |

### Connection Management
```python
# Async (asyncpg example)
import asyncpg

pool: asyncpg.Pool = await asyncpg.create_pool(
    dsn="postgresql://user:pass@host/db",
    min_size=5,
    max_size=20,
    command_timeout=30,
)

async def get_user(user_id: int) -> User | None:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return User(**row) if row else None

# Sync (psycopg)
import psycopg
from psycopg_pool import ConnectionPool

pool = ConnectionPool("postgresql://user:pass@host/db", min_size=5, max_size=20)

def get_user(user_id: int) -> User | None:
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            return User(*row) if row else None
```

### Parameterized Queries (SQL Injection Prevention)
```python
# CORRECT — parameterized
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
cursor.execute("SELECT * FROM users WHERE id = $1", (user_id,))  # asyncpg

# WRONG — string interpolation
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")  # INJECTION!
cursor.execute("SELECT * FROM users WHERE id = " + str(user_id))  # INJECTION!
```

### ORM (SQLAlchemy 2.0+)
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]

engine = create_async_engine("postgresql+asyncpg://user:pass@host/db")
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)

async def create_user(session: AsyncSession, email: str, name: str) -> User:
    user = User(email=email, name=name)
    session.add(user)
    await session.commit()
    return user
```

### Migrations (Alembic)
```bash
# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add users table"

# Apply
alembic upgrade head
```

### Repository Pattern
```python
from abc import ABC, abstractmethod
from typing import Protocol

class UserRepository(Protocol):
    async def get(self, user_id: int) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
    async def save(self, user: User) -> User: ...
    async def delete(self, user_id: int) -> bool: ...

class PostgresUserRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def get(self, user_id: int) -> User | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            return User(**row) if row else None
    
    # ... implement other methods

# Usage (dependency injection)
async def handler(repo: UserRepository, user_id: int):
    user = await repo.get(user_id)
```

### Transactions
```python
# Async
async with pool.acquire() as conn:
    async with conn.transaction():
        await conn.execute("INSERT ...")
        await conn.execute("UPDATE ...")

# SQLAlchemy
async with async_session() as session:
    async with session.begin():
        session.add(user1)
        session.add(user2)
```

---

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| asyncpg for simple scripts | Overhead, complex setup | Use `sqlite3` or `psycopg` |
| SQLAlchemy for hot paths | ORM overhead | Use raw driver |
| Connection pooling for one-shot CLI | Unnecessary overhead | Use direct connection |
| ORM for complex reporting queries | N+1, slow | Use raw SQL |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| String interpolation in SQL | SQL injection | Use parameterized queries |
| N+1 queries | Slow performance | Use joins or batch loading |
| Committing in loops | Slow, partial commits | Batch commit |
| Long-running transactions | Locks, timeouts | Keep transactions short |
| No connection pooling | Connection exhaustion | Use pool |
| Global connection | Thread safety issues | Use DI or thread-local |

### Anti-Pattern

```python
# NEVER: String interpolation in SQL
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")  # INJECTION!

# NEVER: N+1 queries
users = await conn.fetch("SELECT * FROM users")
for user in users:
    orders = await conn.fetch("SELECT * FROM orders WHERE user_id = $1", user["id"])

# NEVER: Committing in loops
for item in items:
    await conn.execute("INSERT INTO ...")
    await conn.commit()  # Slow!

# BETTER: Batch operations
await conn.executemany("INSERT INTO ... VALUES ($1, $2)", items)
await conn.commit()  # Once
```

| Need | Approach |
|------|----------|
| Simple queries, performance critical | Raw driver (`asyncpg`, `psycopg`) |
| Complex domain model, migrations | SQLAlchemy + Alembic |
| Document data | MongoDB (`motor`/`pymongo`) |
| Embedded/local | SQLite (`aiosqlite`/`sqlite3`) |
| Testing | In-memory SQLite or testcontainers |

---

## Preferred Patterns

```python
# Dependency injection for testability
class Database:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.users = PostgresUserRepository(pool)
        self.orders = PostgresOrderRepository(pool)

# Context manager for transactions
@asynccontextmanager
async def transaction(db: Database):
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            yield conn

# Type-safe queries with dataclasses
from dataclasses import dataclass

@dataclass
class UserRow:
    id: int
    email: str
    name: str

async def get_user(conn, user_id: int) -> UserRow | None:
    row = await conn.fetchrow("SELECT id, email, name FROM users WHERE id = $1", user_id)
    return UserRow(**row) if row else None
```

---

## Avoid

- String interpolation in SQL (injection!)
- Global connection/pool (use DI)
- Long-running transactions
- N+1 queries (use joins or batch loading)
- ORM for everything (raw SQL for complex queries)
- No connection pooling
- Committing in loops

---

## Uncertainty Rules

- Check the project's Python version before using `asyncio` database drivers
- Verify installed driver version (asyncpg, psycopg, aiomysql) before using API-specific features
- Inspect `pyproject.toml` or lockfile for database driver versions
- Do not assume SQLAlchemy 2.0 API if project may use 1.x
- Verify connection pool sizing matches database server limits

---

## Verification

- Confirm all SQL queries use parameterized placeholders
- Test with real database (testcontainers or local dev DB)
- Verify connection pool is properly configured (min/max size)
- Test migration up/down produces clean state
- Load test to verify connection limits under stress
- Check for N+1 queries in ORM usage (use `selectinload` or `joinedload`)

---

## Version-Aware Guidance

- **asyncpg**: 0.25+ uses `asyncpg.create_pool()` with `min_size`/`max_size`; older versions use `min_size` only
- **psycopg**: 3.0+ uses `psycopg.AsyncConnection`; 2.x uses `psycopg2`
- **SQLAlchemy**: 2.0+ uses `async_sessionmaker`; 1.x uses `AsyncSession` directly
- **Django**: 4.1+ has native async ORM; older versions need `sync_to_async`
- Check `pyproject.toml` for exact driver versions before using API-specific features

---

## Related Skills

- `security/sql_injection.md`
- `engineering/configuration.md`
- `generation/async_concurrency.md`
- `generation/error_handling.md`
- `testing/organization.md`