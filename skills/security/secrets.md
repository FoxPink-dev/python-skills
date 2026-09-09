# Security: Secrets Management

**Purpose**: Handle secrets (API keys, passwords, tokens) securely.

**When to use**: Any code dealing with credentials or sensitive data.

---

## Core Rules

### Never Hardcode Secrets
```python
# NEVER
API_KEY = "sk_live_abc123"
DB_PASSWORD = "supersecret"

# NEVER in config files committed to git
# config.yaml
# database:
#   password: "supersecret"
```

### Environment Variables
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    jwt_secret: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()  # Loads from env vars + .env
```

### .env File Pattern
```bash
# .env.example (COMMITTED)
DATABASE_URL=postgresql://user:pass@localhost/db
API_KEY=
JWT_SECRET=

# .env (GITIGNORED - local only)
DATABASE_URL=postgresql://prod:realpass@db/prod
API_KEY=sk_live_realkey
JWT_SECRET=supersecretkey
```

### Secret Managers (Production)
```python
# AWS Secrets Manager
import boto3

def get_secret(name: str) -> str:
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=name)
    return response["SecretString"]

# HashiCorp Vault
import hvac

client = hvac.Client(url="https://vault.example.com")
secret = client.secrets.kv.v2.read_secret_version(path="app/config")
```

### In Memory Only
```python
# Don't log secrets
logger.info("Connecting to database", extra={"url": sanitize_url(db_url)})

def sanitize_url(url: str) -> str:
    # postgresql://user:pass@host/db -> postgresql://user:***@host/db
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(url)
    if parsed.password:
        netloc = f"{parsed.username}:***@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"
        return urlunparse(parsed._replace(netloc=netloc))
    return url
```

### Key Rotation
```python
# Support multiple keys for rotation
class Settings(BaseSettings):
    jwt_secrets: list[str] = Field(default_factory=list)  # Current + previous
    current_jwt_secret_index: int = 0
    
    @property
    def jwt_secret(self) -> str:
        return self.jwt_secrets[self.current_jwt_secret_index]
    
    def verify_token(self, token: str) -> dict:
        # Try all secrets for backward compatibility
        for secret in self.jwt_secrets:
            try:
                return jwt.decode(token, secret, algorithms=["HS256"])
            except jwt.InvalidTokenError:
                continue
        raise InvalidTokenError()
```

---

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| Secrets in code | Version control leaks | Environment variables |
| Secrets in Docker images | Image layers persist secrets | Build-time secrets / mounts |
| Single secret without rotation | Compromise = permanent access | Key rotation strategy |
| Secrets in URLs | Logged in access logs | Use headers |
| `.env` committed to git | Secret in version control | `.gitignore` + CI secrets |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Secrets in code | Git history leak | Use env vars / secret manager |
| Secrets in logs | Credential exposure | Sanitize log output |
| Secrets in Docker | Image layer leak | Use `--mount=type=secret` |
| Single key rotation | Old token still valid | Multi-key rotation |
| `.env` committed | Secret in git history | Rotate + rewrite history |
| Secrets in URLs | Logged in access logs | Use `Authorization` header |

### Anti-Pattern

```python
# NEVER: Hardcoded secrets
API_KEY = "sk_live_abc123"  # Leaked in git

# NEVER: Logging secrets
logger.info(f"Connecting with key: {api_key}")

# NEVER: Secrets in URLs
requests.get(f"https://api.example.com?key={api_key}")

# BETTER: Environment + secret manager
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    api_key: str
    model_config = SettingsConfigDict(env_file=".env")
```

| Environment | Approach |
|-------------|----------|
| Local dev | `.env` file (gitignored) |
| CI/CD | Platform secrets (GitHub Actions, GitLab CI) |
| Kubernetes | Secrets + External Secrets Operator |
| Cloud | AWS Secrets Manager, GCP Secret Manager, Azure Key Vault |
| Serverless | Platform env vars + secret manager |

---

## Preferred Patterns

```python
# Single settings instance
_settings: Settings | None = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Dependency injection for testing
def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    app = FastAPI()
    app.state.settings = settings
    return app
```

---

## Avoid

- Committing `.env` with real secrets
- Printing/logging secrets
- Passing secrets in URLs (query params, paths)
- Storing secrets in code (even encoded)
- Single key without rotation plan
- Secrets in Docker images

---

## Validation Considerations

- `git-secrets` / `truffleHog` / `gitleaks` in CI
- No secrets in logs (test with log capture)
- Secret rotation tested
- Least privilege for secret access

---

## Related Skills

- `security/input_validation.md`
- `engineering/configuration.md`
- `engineering/logging.md`
- `engineering/virtual_environments.md`