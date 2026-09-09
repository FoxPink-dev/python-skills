---
name: security_input_validation
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
  - security/sql_injection.md
  - security/command_injection.md
  - security/path_traversal.md
  - security/unsafe_deserialization.md
  - generation/error_handling.md
priority: supporting
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

## Decision Rules

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