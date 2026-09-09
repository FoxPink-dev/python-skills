# Engineering: Configuration

**Purpose**: Application configuration management patterns.

**When to use**: Any application needing configuration (CLI, server, library).

---

## Core Rules

### Configuration Sources (Priority Order)
1. **Defaults** — Code defaults (lowest)
2. **Config file** — TOML/YAML/JSON file
3. **Environment variables** — Override config file
4. **CLI arguments** — Highest priority (for apps)

### Layered Configuration
```python
from dataclasses import dataclass, field
from typing import Optional
import os
from pathlib import Path

@dataclass
class Config:
    # Required (no default)
    database_url: str
    
    # Optional with defaults
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    log_level: str = "INFO"
    
    # Nested config
    redis: "RedisConfig" = field(default_factory=RedisConfig)

@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
```

### Environment Variable Mapping
```python
import os
from dataclasses import fields

from typing import get_type_hints

def load_from_env(config: Config, prefix: str = "APP_") -> Config:
    """Update config from environment variables."""
    hints = get_type_hints(config)  # Resolves string annotations to actual types
    for f in fields(config):
        env_key = f"{prefix}{f.name.upper()}"
        if env_key in os.environ:
            value = os.environ[env_key]
            field_type = hints.get(f.name, str)
            # Handle Optional[X] → extract inner type
            origin = getattr(field_type, "__origin__", None)
            if origin is type(None):
                continue
            if hasattr(field_type, "__args__"):
                # Optional[X] = Union[X, None]
                args = [a for a in field_type.__args__ if a is not type(None)]
                field_type = args[0] if args else str
            # Type conversion
            if field_type is bool:
                value = value.lower() in ("1", "true", "yes", "on")
            elif field_type is int:
                value = int(value)
            elif field_type is float:
                value = float(value)
            elif field_type is list[str]:
                value = value.split(",")
            setattr(config, f.name, value)
    return config
```

### Config File Loading (TOML)
```python
import tomllib  # Python 3.11+

def load_config_file(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)

# For older Python: pip install tomli
```

### Complete Loader
```python
def load_config(
    config_path: Path | None = None,
    env_prefix: str = "APP_",
    cli_overrides: dict | None = None,
) -> Config:
    # 1. Defaults
    config = Config(database_url="")  # Will be validated
    
    # 2. Config file
    if config_path and config_path.exists():
        file_config = load_config_file(config_path)
        apply_dict(config, file_config)
    
    # 3. Environment
    load_from_env(config, env_prefix)
    
    # 4. CLI overrides
    if cli_overrides:
        apply_dict(config, cli_overrides)
    
    # 5. Validate
    validate_config(config)
    
    return config

def apply_dict(config: Config, data: dict) -> None:
    for key, value in data.items():
        if hasattr(config, key):
            setattr(config, key, value)
        elif hasattr(config, key.replace("-", "_")):
            setattr(config, key.replace("-", "_"), value)

def validate_config(config: Config) -> None:
    if not config.database_url:
        raise ValueError("database_url is required")
    if not 1 <= config.port <= 65535:
        raise ValueError("Invalid port")
```

### Pydantic Settings (Alternative)
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings()  # Auto-loads from env + .env
```

---

## Decision Rules

| Need | Approach |
|------|----------|
| Simple app | Dataclass + env vars |
| Complex validation | Pydantic Settings |
| Multiple environments | Config files per env + env vars |
| Secrets | Environment variables only (never files) |
| Feature flags | Config + env override |

---

## Preferred Patterns

```python
# Central config instance
_config: Config | None = None

def get_config() -> Config:
    global _config
    if _config is None:
        _config = load_config()
    return _config

# Reset for testing
def reset_config() -> None:
    global _config
    _config = None
```

---

## Secrets Management

```python
# NEVER hardcode secrets
# NEVER commit .env files with real secrets
# Use: Environment variables, secret managers (AWS Secrets, Vault, etc.)

# .env.example (committed)
DATABASE_URL=postgresql://user:pass@localhost/db
API_KEY=

# .env (gitignored, local only)
DATABASE_URL=postgresql://prod:secret@db/prod
API_KEY=sk-live-...
```

---

## Avoid

- Global mutable config (use frozen dataclass or singleton getter)
- Config file with secrets
- Complex inheritance in config
- Silent failures on missing required config
- Type confusion (env vars are strings)

---

## Validation Considerations

- Test config loading with various sources
- Validate required fields
- Test type conversion edge cases
- Ensure secrets never logged

---

## Related Skills

- `engineering/pyproject_toml.md`
- `engineering/cli_apps.md`
- `security/secrets.md`
- `generation/type_hints.md`
- `generation/error_handling.md`