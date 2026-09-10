---
name: input_validation
purpose: Validate all external input at system boundaries
category: security
triggers:
  - validation
  - input
  - pydantic
  - boundary
  - sanitize
  - allowlist
dependencies:
  - security/command_injection
  - security/unsafe_deserialization
  - generation/error_handling
related:
  - security/sql_injection
  - security/path_traversal
  - security/command_injection
  - testing/regression_tests
priority: critical
estimated_tokens: 1700
---
# Security: Input Validation

**Purpose**: Validate all external input at system boundaries.

**When to use**: All code handling user input, API requests, file uploads, config.

---

## Core Rules

### Validate at Boundaries
```python
# API boundary
@app.post("/users")
def create_user(request: CreateUserRequest) -> UserResponse:
    # Request validated by Pydantic/FastAPI automatically
    return user_service.create(request)

# CLI boundary
def main(args: list[str]) -> int:
    parsed = parse_args(args)  # argparse validates
    config = load_config(parsed.config_file)  # Validates file
    ...

# Config boundary
def load_config(path: Path) -> Config:
    raw = tomllib.load(path)
    return Config.model_validate(raw)  # Pydantic validates
```

### Validation Libraries
| Use Case | Library |
|----------|---------|
| API/Config/Data | `pydantic` (v2) |
| Simple CLI | `argparse` + custom types |
| JSON Schema | `jsonschema` |
| Form data | `wtforms` |

### Pydantic Patterns
```python
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Annotated

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: Annotated[str, Field(min_length=2, max_length=100)]
    age: Annotated[int, Field(ge=13, le=120)]
    tags: list[str] = Field(default_factory=list)
    
    @field_validator("name")
    @classmethod
    def name_no_special_chars(cls, v: str) -> str:
        if not v.replace(" ", "").isalnum():
            raise ValueError("Name must be alphanumeric")
        return v.strip()

# Usage
def create_user(data: CreateUserRequest) -> User:
    # data is guaranteed valid here
    ...
```

### Allowlist Over Blocklist
```python
# GOOD — allowlist
ALLOWED_EXTENSIONS = {".jpg", ".png", ".pdf"}
def validate_extension(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError("file", f"Extension not allowed: {ext}")

# BAD — blocklist (incomplete)
def validate_extension(filename: str) -> None:
    if filename.endswith(".exe"):
        raise ValidationError("file", "Executable not allowed")
    # Misses .bat, .sh, .php, .jar, etc.
```

### Size Limits
```python
# Request body
app = FastAPI()
app.add_middleware(MaxBodySizeMiddleware, max_size=10_000_000)  # 10MB

# File upload
def upload(file: UploadFile) -> None:
    if file.size > MAX_FILE_SIZE:
        raise ValidationError("file", "File too large")
    
    # Stream, don't load entirely
    while chunk := file.read(8192):
        process(chunk)
```

### Sanitization
```python
# HTML output
from markupsafe import escape
safe_html = escape(user_input)

# SQL — use parameterized queries (see sql_injection.md)
# Path — use pathlib.resolve() + is_relative_to() (see path_traversal.md)
# Shell — never use shell=True (see command_injection.md)
```

---

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| Blocklist validation | Incomplete, bypasses new patterns | Allowlist validation |
| Client-side validation only | Can be bypassed | Server-side validation |
| Validation after processing | Injection may succeed before check | Validate at boundary |
| `str.isnumeric()` for validation | Unicode confusion (e.g., `²`) | Use regex or Pydantic |
| Manual string parsing | Error-prone, no type safety | Use Pydantic / argparse |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Blocklist validation | Bypassed by new patterns | Use allowlist |
| No size limits | DoS via huge input | Set max length/size |
| Validation in wrong location | Injection succeeds before check | Validate at boundary |
| Missing Unicode normalization | `café` vs `cafe\u0301` | Normalize with `unicodedata` |
| `str.isdigit()` accepts `²` | Unicode confusion | Use `re.match(r'^\d+$')` |
| Not validating error messages | Leaks internal info | Generic error messages |

### Anti-Pattern

```python
# NEVER: Blocklist validation
def validate_email(email: str) -> bool:
    return "@" in email  # Missing: no domain check, no length limit

# NEVER: Client-side only
# HTML: <input type="email" required>  # No server validation

# NEVER: No size limits
def process(data: str) -> None:
    # data could be gigabytes
    result = data.upper()

# BETTER: Allowlist + size limit + boundary
from pydantic import BaseModel, EmailStr, Field
class Request(BaseModel):
    email: EmailStr  # Built-in validation
    name: str = Field(max_length=100)
```

| Input Type | Validation |
|------------|------------|
| API request | Pydantic model |
| Config file | Pydantic model |
| CLI args | argparse + custom types |
| File upload | Size + type + content validation |
| Database input | ORM/parameterized queries |
| User content (display) | Escape on output |

---

## Preferred Patterns

```python
# Centralized validation
class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

def validate_and_load[T](
    model: type[BaseModel],
    data: dict,
    context: dict | None = None,
) -> T:
    try:
        return model.model_validate(data, context=context)
    except ValidationError as e:
        # Convert to domain exceptions
        errors = e.errors()
        raise ValidationError(errors[0]["loc"][0], errors[0]["msg"]) from e
```

---

## Avoid

- Trusting any external input
- Validation only in UI (client-side only)
- Blocklist-based validation
- No size limits on uploads/requests
- Manual string parsing for structured data

---

## Validation Considerations

- Test with malicious inputs (injection, oversized, malformed)
- Fuzz testing for parsers
- Validate error messages don't leak info

---

## Related Skills

- `security/sql_injection.md`
- `security/command_injection.md`
- `security/path_traversal.md`
- `security/unsafe_deserialization.md`
- `generation/error_handling.md`