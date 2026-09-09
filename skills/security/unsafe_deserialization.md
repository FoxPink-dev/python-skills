# Security: Unsafe Deserialization Prevention

**Purpose**: Prevent code execution via deserialization of untrusted data.

**When to use**: Loading pickles, YAML, JSON with custom decoders, any serialized data.

---

## Core Rules

### Never Deserialize Untrusted Data with Unsafe Formats
```python
# NEVER — pickle executes arbitrary code
import pickle
data = pickle.loads(untrusted_bytes)  # RCE!

# NEVER — yaml.load without SafeLoader
import yaml
data = yaml.load(untrusted_string)  # RCE!

# NEVER — shelve (uses pickle)
import shelve
db = shelve.open(untrusted_file)

# NEVER — dill, cloudpickle, marshal
```

### Safe Alternatives
| Unsafe | Safe Replacement |
|--------|------------------|
| `pickle` | `json`, `msgpack`, `orjson`, `cbor2` |
| `yaml.load()` | `yaml.safe_load()` |
| `shelve` | `sqlite3` + `json` |
| Custom `__reduce__` | Don't accept serialized objects |

### If You Must Use Pickle (Internal Only)
```python
# ONLY for trusted internal data
# Add integrity verification
import hmac
import hashlib

def sign_data(data: bytes, key: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()

def verify_and_load(data: bytes, signature: bytes, key: bytes) -> Any:
    if not hmac.compare_digest(sign(data, key), signature):
        raise SecurityError("Invalid signature")
    return pickle.loads(data)  # Still risky if key compromised
```

### YAML Safe Loading
```python
import yaml

# ALWAYS use safe_load
data = yaml.safe_load(untrusted_string)

# Or explicit SafeLoader
data = yaml.load(untrusted_string, Loader=yaml.SafeLoader)

# NEVER
data = yaml.load(untrusted_string)  # Default Loader is unsafe!
data = yaml.load(untrusted_string, Loader=yaml.Loader)  # Unsafe!
data = yaml.load(untrusted_string, Loader=yaml.FullLoader)  # Still unsafe!
```

### JSON Safety
```python
import json

# json module is SAFE — no code execution
data = json.loads(untrusted_string)

# But: watch for DoS (deeply nested, huge objects)
# Use limits if needed
import sys
json.loads(huge_string)  # Can consume memory
```

### Custom Decoders (Risk)
```python
# Dangerous if hook executes code
def dangerous_hook(d):
    if "__class__" in d:
        return globals()[d["__class__"]](**d)  # RCE!
    return d

json.loads(untrusted, object_hook=dangerous_hook)  # NEVER

# Safe: only transform data, no execution
def safe_hook(d):
    if "created_at" in d:
        d["created_at"] = datetime.fromisoformat(d["created_at"])
    return d
```

---

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| Pickle for cross-process IPC | Shared memory/mmap faster, no exec risk | `multiprocessing.shared_memory` |
| Pickle for cache | Slow, deserialization RCE risk | `json` or `msgpack` |
| YAML for config | YAML parsing is complex, `yaml.safe_load()` limits | TOML (`tomllib`) |
| `shelve` for database | Uses pickle internally, no concurrent access | `sqlite3` |
| `marshal` for bytecode | CPython internal, no stability guarantee | Don't use directly |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| `yaml.load()` without SafeLoader | Arbitrary code execution | Use `yaml.safe_load()` |
| Pickle on untrusted data | RCE via crafted payload | Use JSON/msgpack |
| `yaml.FullLoader` still unsafe | Can instantiate arbitrary objects | Use `yaml.SafeLoader` |
| Signing pickle data | Key compromise = RCE | Avoid pickle entirely for external data |
| `json.loads` with deep nesting | DoS via stack overflow | Limit recursion depth |
| Custom `object_hook` instantiating | RCE via crafted JSON | Only transform data types, no instantiation |

### Anti-Pattern

```python
# NEVER: Pickle for any data that may be tampered with
import pickle
data = pickle.loads(untrusted_bytes)  # Can execute arbitrary code

# NEVER: yaml.load with default loader
data = yaml.load(untrusted_string)  # Uses FullLoader by default

# NEVER: yaml.FullLoader (still unsafe)
data = yaml.load(untrusted_string, Loader=yaml.FullLoader)  # Can create objects
```

| Format | Trusted Internal | Untrusted External |
|--------|------------------|-------------------|
| JSON | ✓ | ✓ (with size limits) |
| YAML (safe_load) | ✓ | ✓ |
| MessagePack | ✓ | ✓ |
| CBOR | ✓ | ✓ |
| Pickle | ✓ (with signing) | ✗ NEVER |
| Shelve | ✓ | ✗ |
| Custom pickle | ✓ (with signing) | ✗ NEVER |

---

## Preferred Patterns

```python
# Config loading — use safe format
def load_config(path: Path) -> Config:
    if path.suffix == ".json":
        return Config.model_validate(json.loads(path.read_text()))
    elif path.suffix in (".yaml", ".yml"):
        return Config.model_validate(yaml.safe_load(path.read_text()))
    elif path.suffix == ".toml":
        import tomllib
        return Config.model_validate(tomllib.loads(path.read_text()))
    else:
        raise ValueError("Unsupported config format")

# Cache — use safe serialization
def cache_get(key: str) -> Any | None:
    data = redis.get(key)
    if data:
        return json.loads(data)
    return None

def cache_set(key: str, value: Any, ttl: int) -> None:
    redis.setex(key, ttl, json.dumps(value, default=json_default))
```

---

## Avoid

- `pickle` for any external data
- `yaml.load()` without `SafeLoader`
- Custom `object_hook` that instantiates classes
- Storing serialized objects in database for later deserialization
- Assuming "internal" data stays internal forever

---

## Validation Considerations

- `bandit` B301, B506 checks
- Dependency scan for pickle usage
- Penetration testing deserialization endpoints

---

## Related Skills

- `security/input_validation.md`
- `stdlib/json.md`
- `engineering/configuration.md`