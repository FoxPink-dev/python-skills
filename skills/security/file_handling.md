# Security: File Handling

**Purpose**: Safe file operations to prevent information disclosure and corruption.

**When to use**: Reading, writing, uploading, serving files.

---

## Core Rules

### Atomic Writes
```python
import tempfile
from pathlib import Path

def atomic_write(path: Path, content: str | bytes, encoding: str = "utf-8") -> None:
    """Write atomically to prevent partial reads."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temp file in same directory (same filesystem)
    with tempfile.NamedTemporaryFile(
        mode="w" if isinstance(content, str) else "wb",
        dir=path.parent,
        delete=False,
        encoding=encoding if isinstance(content, str) else None,
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    
    # Atomic replace
    tmp_path.replace(path)

# Usage
atomic_write(Path("config.json"), json.dumps(config))
```

### Safe File Reading
```python
def read_file_safe(path: Path, max_size: int = 10_000_000) -> bytes:
    """Read file with size limit."""
    stat = path.stat()
    if stat.st_size > max_size:
        raise ValueError(f"File too large: {stat.st_size} > {max_size}")
    
    return path.read_bytes()

def read_text_safe(path: Path, encoding: str = "utf-8", max_size: int = 1_000_000) -> str:
    return read_file_safe(path, max_size).decode(encoding)
```

### Temporary Files
```python
import tempfile

# GOOD — secure temp file
with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
    tmp.write(data)
    tmp_path = Path(tmp.name)
try:
    process(tmp_path)
finally:
    tmp_path.unlink(missing_ok=True)

# BETTER — TemporaryDirectory (auto cleanup)
with tempfile.TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir) / "file.txt"
    tmp_path.write_text(data)
    process(tmp_path)
# Auto cleanup on exit
```

### Permissions
```python
# Don't make world-writable
path.write_text(content)
path.chmod(0o600)  # Owner read/write only

# For secrets
path.write_text(secret)
path.chmod(0o400)  # Owner read only
```

### Path Validation (Recap)
```python
# Always validate before operations
def serve_file(user_path: str, root: Path) -> FileResponse:
    safe = safe_path(user_path, root)  # From path_traversal.md
    if not safe.is_file():
        raise FileNotFoundError()
    return FileResponse(safe)
```

---

## Decision Rules

| Operation | Pattern |
|-----------|---------|
| Write config/data | Atomic write (temp + replace) |
| Read untrusted file | Size limit + validation |
| Temp processing | `TemporaryDirectory` |
| Upload handling | Validate name, size, type, stream write |
| Log rotation | `RotatingFileHandler` |

---

## Preferred Patterns

```python
class SafeFileManager:
    def __init__(self, base_dir: Path, max_file_size: int = 10_000_000):
        self.base_dir = base_dir.resolve()
        self.max_size = max_file_size
    
    def write(self, rel_path: str, content: str | bytes) -> Path:
        path = self._validate(rel_path)
        atomic_write(path, content)
        return path
    
    def read(self, rel_path: str) -> bytes:
        path = self._validate(rel_path)
        return read_file_safe(path, self.max_size)
    
    def _validate(self, rel_path: str) -> Path:
        requested = (self.base_dir / rel_path).resolve()
        if not requested.is_relative_to(self.base_dir):
            raise SecurityError("Path traversal")
        return requested
```

---

## Avoid

- Direct writes to final path (partial reads possible)
- No size limits on reads
- World-writable files
- Predictable temp file names
- Leaving temp files behind

---

## Validation Considerations

- Test concurrent writes (atomicity)
- Test size limit enforcement
- Test path traversal attempts
- Test cleanup on exception

---

## Related Skills

- `security/path_traversal.md`
- `security/secrets.md`
- `stdlib/pathlib.md`