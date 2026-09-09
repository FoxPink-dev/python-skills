# Security: Path Traversal Prevention

**Purpose**: Prevent directory traversal attacks when handling file paths.

**When to use**: File uploads, path parameters, file serving, archive extraction.

---

## Core Rules

### Always Resolve and Validate
```python
from pathlib import Path

def safe_path(user_input: str, base_dir: Path) -> Path:
    """Resolve path and ensure it's within base directory."""
    base = base_dir.resolve()
    requested = (base / user_input).resolve()
    
    # Critical: check AFTER resolve (handles symlinks)
    if not requested.is_relative_to(base):
        raise ValueError(f"Path traversal attempt: {user_input}")
    
    return requested

# Usage
@app.get("/files/{path:path}")
def serve_file(path: str):
    safe = safe_path(path, FILES_ROOT)
    return FileResponse(safe)
```

### Common Attack Vectors
```python
# These all attempt to escape:
"../../etc/passwd"
"..\\..\\windows\\system32"
"%2e%2e%2f"  # URL encoded
"....//"     # Double dots
"subdir/../../etc/passwd"
"symlink_to_root/target"
```

### Archive Extraction (Critical)
```python
import tarfile
import zipfile

def safe_extract_tar(tar_path: Path, dest: Path) -> None:
    dest = dest.resolve()
    with tarfile.open(tar_path) as tar:
        for member in tar.getmembers():
            member_path = (dest / member.name).resolve()
            if not member_path.is_relative_to(dest):
                raise ValueError(f"Path traversal in archive: {member.name}")
        tar.extractall(dest)  # Safe after validation

def safe_extract_zip(zip_path: Path, dest: Path) -> None:
    dest = dest.resolve()
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            member_path = (dest / name).resolve()
            if not member_path.is_relative_to(dest):
                raise ValueError(f"Path traversal in archive: {name}")
        zf.extractall(dest)
```

### File Upload
```python
def save_upload(file: UploadFile, upload_dir: Path) -> Path:
    # Validate filename
    filename = Path(file.filename).name  # Strip directory components
    if not filename:
        raise ValueError("Invalid filename")
    
    # Allowlist extension
    allowed = {".jpg", ".png", ".pdf", ".txt"}
    if filename.suffix.lower() not in allowed:
        raise ValueError("File type not allowed")
    
    # Generate safe name (UUID + extension)
    safe_name = f"{uuid4()}{filename.suffix.lower()}"
    dest = safe_path(safe_name, upload_dir)
    
    # Stream write (memory efficient)
    with dest.open("wb") as f:
        while chunk := file.file.read(8192):
            f.write(chunk)
    
    return dest
```

### Symlink Safety
```python
def read_file_safe(path: Path, base: Path) -> bytes:
    """Read file, following symlinks but validating final target."""
    resolved = path.resolve()
    base_resolved = base.resolve()
    
    if not resolved.is_relative_to(base_resolved):
        raise ValueError("Path traversal via symlink")
    
    # Optional: reject symlinks entirely
    if path.is_symlink():
        raise ValueError("Symlinks not allowed")
    
    return resolved.read_bytes()
```

---

## Decision Rules

| Operation | Protection |
|-----------|------------|
| Serve static file | `safe_path` + `is_relative_to` |
| User upload | Strip path, allowlist ext, UUID name |
| Archive extract | Validate each member before extract |
| Config file read | Fixed known paths only |
| Temp file | `tempfile.mkstemp` (secure) |

---

## Preferred Patterns

```python
# Centralized path validator
class PathValidator:
    def __init__(self, base: Path):
        self.base = base.resolve()
    
    def validate(self, user_path: str | Path) -> Path:
        requested = (self.base / user_path).resolve()
        if not requested.is_relative_to(self.base):
            raise SecurityError("Path traversal attempt")
        return requested
    
    def validate_exists(self, user_path: str | Path) -> Path:
        path = self.validate(user_path)
        if not path.exists():
            raise FileNotFoundError(path)
        return path
```

---

## Avoid

- `os.path.join` without validation
- `Path(user_input)` directly
- `../` in user-controlled paths
- Extracting archives without member validation
- Serving files from user input without validation

---

## Validation Considerations

- Test with traversal payloads
- Test with symlinks
- Test with URL encoding
- Test with null bytes (`\0`)
- `bandit` B108, B306 checks

---

## Related Skills

- `security/command_injection.md`
- `security/input_validation.md`
- `stdlib/pathlib.md`
- `stdlib/subprocess.md`