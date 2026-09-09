# Security: SQL Injection Prevention

**Purpose**: Prevent SQL injection through proper query parameterization.

**When to use**: All database interactions.

---

## Core Rules

### Always Use Parameterized Queries
```python
# CORRECT — asyncpg
async with pool.acquire() as conn:
    await conn.execute(
        "INSERT INTO users (email, name) VALUES ($1, $2)",
        email, name
    )

# CORRECT — psycopg
with conn.cursor() as cur:
    cur.execute(
        "INSERT INTO users (email, name) VALUES (%s, %s)",
        (email, name)
    )

# CORRECT — SQLAlchemy
session.execute(
    text("SELECT * FROM users WHERE email = :email"),
    {"email": email}
)

# CORRECT — ORM
User.query.filter_by(email=email).first()
```

### Never Use String Interpolation
```python
# WRONG — SQL INJECTION!
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
cursor.execute("SELECT * FROM users WHERE id = " + str(user_id))

# WRONG — .format()
cursor.execute("SELECT * FROM users WHERE email = '{}'".format(email))
```

### Dynamic Queries (Safe Patterns)
```python
# WHERE IN with variable length
ids = [1, 2, 3]
placeholders = ", ".join(["%s"] * len(ids))
query = f"SELECT * FROM users WHERE id IN ({placeholders})"
cursor.execute(query, ids)  # Parameters still parameterized!

# Optional filters
conditions = []
params = []
if name:
    conditions.append("name ILIKE %s")
    params.append(f"%{name}%")
if email:
    conditions.append("email = %s")
    params.append(email)

query = "SELECT * FROM users"
if conditions:
    query += " WHERE " + " AND ".join(conditions)
cursor.execute(query, params)
```

### ORM Safety
```python
# SQLAlchemy — safe
User.query.filter(User.email == email).all()
session.query(User).filter_by(email=email).first()

# Django — safe
User.objects.filter(email=email)

# Unsafe in ORM — raw()
User.objects.raw("SELECT * FROM users WHERE email = '%s'" % email)  # BAD!
User.objects.raw("SELECT * FROM users WHERE email = %s", [email])   # GOOD
```

### Identifier Quoting (Table/Column Names)
```python
# Can't parameterize identifiers — validate against allowlist
ALLOWED_TABLES = {"users", "orders", "products"}
ALLOWED_COLUMNS = {"id", "email", "name", "created_at"}

def query_table(table: str, column: str, value: str):
    if table not in ALLOWED_TABLES:
        raise ValueError("Invalid table")
    if column not in ALLOWED_COLUMNS:
        raise ValueError("Invalid column")
    
    # Safe: validated identifiers
    query = f"SELECT * FROM {table} WHERE {column} = %s"
    cursor.execute(query, (value,))
```

---

## Decision Rules

| Query Type | Safe Pattern |
|------------|--------------|
| Static query | Parameterized |
| Dynamic WHERE | Build conditions, parameterize values |
| IN clause | Generate placeholders, parameterize values |
| Table/column names | Allowlist validation |
| Complex reporting | Views / stored procedures / CTEs |

---

## Preferred Patterns

```python
# Repository pattern encapsulates safety
class UserRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def find_by_email(self, email: str) -> User | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1",
                email
            )
            return User(**row) if row else None
    
    async def search(
        self,
        name: str | None = None,
        email: str | None = None,
        limit: int = 100,
    ) -> list[User]:
        conditions = []
        params = []
        param_num = 1
        
        if name:
            conditions.append(f"name ILIKE ${param_num}")
            params.append(f"%{name}%")
            param_num += 1
        if email:
            conditions.append(f"email = ${param_num}")
            params.append(email)
            param_num += 1
        
        query = "SELECT * FROM users"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += f" LIMIT ${param_num}"
        params.append(limit)
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [User(**row) for row in rows]
```

---

## Avoid

- Any string concatenation in SQL
- `f-strings` in SQL
- `.format()` in SQL
- `%` formatting in SQL (except parameterized drivers)
- Dynamic ORDER BY without validation

---

## Validation Considerations

- Code review: grep for `f"SELECT` `f"INSERT` `f"UPDATE` `f"DELETE`
- `bandit` SQL injection checks
- SQLMap testing
- ORM raw query audit

---

## Related Skills

- `security/input_validation.md`
- `engineering/database.md`
- `generation/error_handling.md`