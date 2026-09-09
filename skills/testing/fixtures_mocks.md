# Testing: Fixtures and Mocks

**Purpose**: Effective test fixtures and mocking strategies.

**When to use**: Writing tests that need setup, dependencies, or isolation.

---

## Core Rules

### Fixture Principles
- **Scope appropriately**: `function` (default), `class`, `module`, `session`
- **Single responsibility**: Each fixture does one thing
- **Explicit dependencies**: Fixtures request what they need
- **Cleanup**: Use `yield` for teardown

### Fixture Patterns

```python
# conftest.py

# Session-scoped expensive resource
@pytest.fixture(scope="session")
def database():
    db = create_test_database()
    yield db
    db.drop()

# Function-scoped clean state
@pytest.fixture
def clean_db(database):
    database.truncate_all()
    yield database
    database.truncate_all()

# Factory fixture
@pytest.fixture
def user_factory(clean_db):
    def _create(email: str = "test@test.com", **kwargs):
        return UserService(clean_db).create(email, **kwargs)
    return _create

# Parametrized fixture
@pytest.fixture(params=["sqlite", "postgresql"])
def db_engine(request):
    if request.param == "sqlite":
        return create_sqlite_engine()
    return create_pg_engine()
```

### Mocking Guidelines

```python
# Mock at the boundary (where your code calls external code)
# NOT deep in the call stack

# GOOD — mock the client your code uses
@patch("mypackage.services.payment.StripeClient")
def test_charge(mock_stripe, payment_service):
    mock_stripe.return_value.charge.return_value = ChargeResult(success=True)
    result = payment_service.charge(100, "token")
    assert result.success

# BAD — mock internal implementation
@patch("mypackage.services.payment.calculate_fee")
def test_charge_bad(mock_fee, payment_service):
    ...
```

### Mock Types
```python
from unittest.mock import Mock, MagicMock, AsyncMock, PropertyMock

# Sync mock
mock = Mock()
mock.method.return_value = "value"
mock.method.side_effect = Exception("error")
mock.property = PropertyMock(return_value="value")

# Async mock
async_mock = AsyncMock()
async_mock.async_method.return_value = "value"
async_mock.async_method.side_effect = [val1, val2, Exception("error")]

# Spec (prevents typos)
mock = Mock(spec=RealClass)
mock.real_method()  # OK
mock.typo_method()  # AttributeError!

# Autospec (signature checking)
mock = Mock(autospec=RealClass)
mock.real_method(1, 2)  # OK
mock.real_method()      # TypeError: missing args
```

### Test Data Builders
```python
# For complex test objects
class UserBuilder:
    def __init__(self):
        self._email = "test@test.com"
        self._name = "Test User"
        self._active = True
        self._roles = []
    
    def with_email(self, email: str) -> "UserBuilder":
        self._email = email
        return self
    
    def with_name(self, name: str) -> "UserBuilder":
        self._name = name
        return self
    
    def inactive(self) -> "UserBuilder":
        self._active = False
        return self
    
    def with_roles(self, *roles) -> "UserBuilder":
        self._roles = list(roles)
        return self
    
    def build(self) -> User:
        return User(
            email=self._email,
            name=self._name,
            active=self._active,
            roles=self._roles,
        )

# Usage
def test_admin_user(user_factory):
    admin = UserBuilder().with_roles("admin").build()
    assert admin.has_permission("admin")
```

---

## Decision Rules

| Need | Fixture/Mock Pattern |
|------|---------------------|
| Shared expensive resource | `scope="session"` fixture |
| Clean state per test | Function fixture with cleanup |
| Test data variations | Factory fixture or builder |
| External service | Mock at boundary |
| Time-dependent | `freezegun` / mock `time.time` |
| Random-dependent | Mock `random` / `secrets` |
| Multiple implementations | Parametrized fixture |

---

## Preferred Patterns

```python
# Conftest organization
# tests/conftest.py — project-wide
# tests/unit/conftest.py — unit-specific
# tests/integration/conftest.py — integration-specific

# Fixture naming
@pytest.fixture
def user_service() -> UserService:  # Return type hint
    ...

# Async fixtures
@pytest.fixture
async def async_client() -> AsyncClient:
    client = AsyncClient()
    yield client
    await client.aclose()

# Mock fixture
@pytest.fixture
def mock_email_service() -> Mock:
    return Mock(spec=EmailService)
```

---

## Avoid

- Fixtures with side effects (no cleanup)
- Over-mocking (mock everything, test nothing)
- Mocking stdlib you should use directly (`json`, `os.path`, `pathlib`)
- Fixtures that depend on test order
- Complex fixture chains (>3 levels)

---

## Validation Considerations

- Fixture setup/teardown time (profile with `--durations=10`)
- Mock call verification (`assert_called_once_with`)
- No real network calls in unit tests (use `pytest-mock` + `requests-mock`)

---

## Related Skills

- `testing/organization.md`
- `testing/parameterized.md`
- `testing/async_tests.md`
- `generation/error_handling.md`