# Stdlib: pathlib

**Purpose**: Modern, object-oriented filesystem paths.

**When to use**: All filesystem operations. Replaces `os.path`, `os.walk`, `glob`.

---

## Core Rules

### Path Objects
```python
from pathlib import Path

# Creation
Path("relative/path")
Path("/absolute/path")
Path.home() / "documents"
Path.cwd()

# From parts
Path("a", "b", "c")  # a/b/c
```

### Properties
```python
p = Path("a/b/c.txt")

p.name        # "c.txt"
p.stem        # "c"
p.suffix      # ".txt"
p.suffixes    # [".txt"]
p.parent      # Path("a/b")
p.parents     # [Path("a/b"), Path("a"), Path(".")]
p.anchor      # "" (or "/" on Unix, "C:\\" on Windows)
p.root        # "/" or "C:\\"
p.drive       # "" or "C:"
```

### Navigation
```python
p / "subdir" / "file.txt"     # Join
p.joinpath("sub", "file.txt") # Join (multiple args)
p.resolve()                    # Absolute, resolve symlinks
p.absolute()                   # Absolute (no symlink resolve)
p.relative_to(Path("a"))       # Relative path (raises if not subpath)
p.is_relative_to(Path("a"))    # Boolean check (Python 3.9+)
```

### Filesystem Operations
```python
p.exists()           # Exists (file, dir, symlink)
p.is_file()          # Regular file
p.is_dir()           # Directory
p.is_symlink()       # Symlink
p.is_absolute()      # Absolute path
p.is_relative()      # Relative path (Python 3.13+)

p.stat()             # os.stat_result
p.lstat()            # Don't follow symlinks
p.owner()            # Owner name
p.group()            # Group name

# Times (float seconds since epoch)
p.stat().st_mtime    # Modified
p.stat().st_atime    # Accessed
p.stat().st_ctime    # Created (Unix: metadata change)
```

### Reading/Writing
```python
# Text
text = p.read_text(encoding="utf-8")
p.write_text("content", encoding="utf-8")

# Binary
data = p.read_bytes()
p.write_bytes(b"content")

# Open (returns file object)
with p.open("r", encoding="utf-8") as f:
    ...

# Append
p.write_text("more", encoding="utf-8", mode="a")
```

### Directory Operations
```python
p.mkdir(parents=True, exist_ok=True)  # Create dir (mkdir -p)
p.rmdir()                              # Remove empty dir
p.unlink(missing_ok=True)              # Remove file (missing_ok Python 3.8+)
p.replace(target)                      # Atomic replace
p.rename(target)                       # Rename (not atomic across fs)
p.symlink_to(target)                   # Create symlink
p.hardlink_to(target)                  # Create hardlink
p.touch(exist_ok=True)                 # Create empty file / update mtime
```

### Iteration and Globbing
```python
# Iterate directory
for child in p.iterdir():
    ...

# Glob patterns
for match in p.glob("*.py"):           # Non-recursive
    ...
for match in p.rglob("*.py"):          # Recursive
    ...

# Walk (like os.walk)
for root, dirs, files in p.walk():
    ...
```

### Path Matching
```python
p.match("*.py")              # Match final component
p.match("*/*.py")            # Match relative pattern
```

### Temporary Files
```python
import tempfile

with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
    path = Path(f.name)
    # Use path
# Cleanup manual or use context manager

# Better: tempfile.TemporaryDirectory
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "file.txt"
    ...
# Auto cleanup
```

---

## Decision Rules

| Operation | pathlib Method |
|-----------|----------------|
| Join paths | `p / "name"` or `p.joinpath()` |
| Get parent | `p.parent` |
| Get filename | `p.name` |
| Get extension | `p.suffix` / `p.suffixes` |
| Read text file | `p.read_text(encoding="utf-8")` |
| Write text file | `p.write_text(content, encoding="utf-8")` |
| Read binary | `p.read_bytes()` |
| Write binary | `p.write_bytes(data)` |
| Create dirs | `p.mkdir(parents=True, exist_ok=True)` |
| Delete file | `p.unlink(missing_ok=True)` |
| Delete empty dir | `p.rmdir()` |
| List directory | `p.iterdir()` |
| Find files | `p.glob()` / `p.rglob()` |
| Walk tree | `p.walk()` |
| Atomic write | Write to temp, `p.replace(target)` |

---

## Preferred Patterns

```python
# Atomic write (prevents partial reads)
def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding=encoding)
    tmp.replace(path)

# Safe config loading
def load_config(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

# Recursive find with filter
py_files = list(project_root.rglob("*.py"))
```

---

## Avoid

- `os.path` functions (use pathlib equivalents)
- String manipulation for paths (`+` or `os.path.join`)
- `glob.glob()` (use `Path.glob()` / `rglob()`)
- `os.walk()` (use `Path.walk()`)
- Not specifying `encoding` in text operations
- `missing_ok=False` (default) — raises on missing file

---

## Windows Notes

- `Path` handles `\` and `/` correctly
- `p.drive` returns `"C:"` on Windows
- `p.anchor` returns `"C:\\"` on Windows
- Symlinks require admin or Developer Mode
- Case-insensitive filesystem

---

## Validation Considerations

- Type checkers understand `Path` methods
- `Path` implements `os.PathLike` — works with stdlib APIs
- `resolve()` may raise on broken symlinks

---

## Related Skills

- `stdlib/os_sys.md`
- `engineering/configuration.md`
- `security/path_traversal.md`
- `security/file_handling.md`