# Stdlib: json

**Purpose**: JSON encoding/decoding with Python objects.

**When to use**: Serialization, config, APIs, data exchange.

---

## Core Rules

### Basic Usage
```python
import json

# Encode
json_str = json.dumps(obj, indent=2, ensure_ascii=False)
json_bytes = json.dumps(obj).encode("utf-8")

# Decode
obj = json.loads(json_str)
obj = json.load(file_obj)
```

### Default Serialization
| Python | JSON |
|--------|------|
| `dict` | object |
| `list`, `tuple` | array |
| `str` | string |
| `int`, `float` | number |
| `True`, `False` | `true`, `false` |
| `None` | `null` |

### Custom Serialization
```python
# default= callable for unsupported types
json.dumps(obj, default=lambda o: o.isoformat() if hasattr(o, "isoformat") else str(o))

# Or subclass JSONEncoder
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

json.dumps(obj, cls=CustomEncoder)
```

### Custom Deserialization
```python
# object_hook for dicts
def decode_datetime(d):
    for key, value in d.items():
        if key.endswith("_at") and isinstance(value, str):
            try:
                d[key] = datetime.fromisoformat(value)
            except ValueError:
                pass
    return d

json.loads(json_str, object_hook=decode_datetime)

# object_pairs_hook for ordered pairs (preserves duplicate keys)
json.loads(json_str, object_pairs_hook=OrderedDict)
```

### Streaming (Large Data)
```python
# Incremental encoding
encoder = json.JSONEncoder()
for chunk in encoder.iterencode(large_obj):
    write(chunk)

# Incremental decoding
decoder = json.JSONDecoder()
for obj in decoder.raw_decode(stream):
    ...
```

---

## Decision Rules

| Situation | Approach |
|-----------|----------|
| Simple dict/list | `json.dumps` / `json.loads` |
| Datetime, UUID, Decimal | Custom `JSONEncoder` + `object_hook` |
| Large data (streaming) | `JSONEncoder.iterencode` / `JSONDecoder.raw_decode` |
| Preserve order | Default (Python 3.7+) or `object_pairs_hook` |
| Non-ASCII chars | `ensure_ascii=False` |
| Compact output | `separators=(",", ":")` |
| Human-readable | `indent=2` |

---

## Preferred Patterns

```python
# Standard API response
def to_json(data: Any) -> str:
    return json.dumps(
        data,
        default=json_default,
        ensure_ascii=False,
        separators=(",", ":"),
    )

def json_default(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        return str(obj)
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

# Safe loading with schema validation
def load_json(path: Path, schema: type) -> Any:
    data = json.loads(path.read_text(encoding="utf-8"))
    # Validate with pydantic, attrs, or manual check
    return validate(data, schema)
```

---

## Security

- **Never** use `json.load` on untrusted input without validation
- `json` module is safe (no code execution) unlike `pickle`/`yaml`
- Large inputs can cause DoS (billions of nested objects) — consider `defusedxml`-style limits
- `object_hook` runs on every dict — avoid expensive operations

---

## Avoid

- `pickle` for data exchange (unsafe, Python-specific)
- `yaml.load` without `Loader=yaml.SafeLoader` (unsafe)
- Custom encoders that mutate input
- `default=str` (silently converts everything to string, loses type info)
- Large `indent` in production (wastes bandwidth)

---

## Validation Considerations

- Schema validation after decode (pydantic, jsonschema, manual)
- Round-trip test: `json.loads(json.dumps(obj)) == obj`
- `json.JSONDecodeError` for parse errors (includes position)

---

## Related Skills

- `security/unsafe_deserialization.md`
- `engineering/configuration.md`
- `stdlib/datetime.md`
- `generation/type_hints.md` (TypedDict for JSON shapes)