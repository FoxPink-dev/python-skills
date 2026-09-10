---
name: file_handling
purpose: Safe file operations to prevent information disclosure and corruption
category: security
triggers:
  - file
  - read
  - write
  - upload
  - atomic
  - temp
dependencies:
  - security/path_traversal
  - security/secrets
  - stdlib/pathlib
related:
  - security/path_traversal
  - security/input_validation
  - testing/regression_tests
priority: high
estimated_tokens: 1400
---
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

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| Direct write to final path | Partial reads on crash | Atomic write (temp + rename) |
| No file size limit | DoS via huge files | Set `max_size` parameter |
| World-writable files | Security risk | `chmod 0o600` or `0o640` |
| Predictable temp file names | Race condition / symlink attack | Use `tempfile` module |
| `open()` without encoding | Platform-dependent default | Specify `encoding="utf-8"` |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Direct write to final path | Partial reads on crash | Atomic write (temp + rename) |
| No file size limit | DoS via huge files | Set `max_size` parameter |
| World-writable files | Other users can modify | `chmod 0o600` |
| Predictable temp names | Race condition | Use `tempfile.NamedTemporaryFile` |
| Missing encoding | UnicodeDecodeError on read | Specify `encoding="utf-8"` |
| Not closing file handles | Resource leak | Use `with` statement |
| TOCTOU race | File changes between check and use | Open immediately, handle errors |

### Anti-Pattern

```python
# NEVER: Direct write (partial reads on crash)
with open("config.json", "w") as f:
    json.dump(config, f)  # Crash = corrupt file

# NEVER: World-writable
path.write_text(data)
path.chmod(0o666)  # Anyone can modify

# NEVER: Predictable temp name
temp_path = Path("/tmp/myapp_data.txt")  # Symlink attack possible

# BETTER: Atomic write
def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)
```

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

## Change Scope

- Prefer the smallest correct change to file handling code
- Preserve existing file paths and naming conventions unless task requires otherwise
- Do not refactor unrelated file handling code
- Preserve existing permission and ownership semantics
- Avoid changing file size limits without explicit approval

---

## Verification

- Test concurrent writes for atomicity
- Test size limit enforcement
- Test path traversal attempts are blocked
- Test cleanup on exception (temp files removed)
- Verify atomic write pattern (write to temp, then rename)

---

## Related Skills

- `security/path_traversal.md`
- `security/secrets.md`
- `stdlib/pathlib.md`