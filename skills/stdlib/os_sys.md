# Stdlib: os and sys

**Purpose**: Operating system interfaces and Python runtime.

**When to use**: Process environment, filesystem, Python internals. Prefer `pathlib` for paths.

---

## Core Rules

### os — Environment and Process
```python
import os

# Environment variables
os.environ              # Mapping (str -> str)
os.getenv("KEY", "default")
os.environ["KEY"] = "value"   # Set
del os.environ["KEY"]         # Unset

# Process
os.getpid()             # Current PID
os.getppid()            # Parent PID
os.cpu_count()          # CPU count
os.urandom(n)           # Cryptographic random bytes

# Working directory
os.getcwd()             # Str
os.chdir(path)          # Change

# Filesystem (prefer pathlib)
os.listdir(path)        # Names only
os.scandir(path)        # DirEntry objects (efficient)
os.makedirs(path, exist_ok=True)
os.remove(path)
os.rmdir(path)
os.rename(src, dst)
os.replace(src, dst)    # Atomic
os.symlink(src, dst)
os.readlink(path)
os.stat(path)           # stat_result
os.path.isfile(path)    # Legacy — use pathlib

# Path manipulation (legacy — use pathlib)
os.path.join(*parts)
os.path.split(path)
os.path.dirname(path)
os.path.basename(path)
os.path.splitext(path)
os.path.abspath(path)
os.path.relpath(path, start)
os.path.normpath(path)
os.path.expanduser("~/path")
os.path.expandvars("$VAR/path")
```

### sys — Python Runtime
```python
import sys

# Version
sys.version             # String
sys.version_info        # Named tuple (major, minor, micro, ...)
sys.version_info >= (3, 12)

# Paths
sys.path                # Module search path (list)
sys.prefix              # Install prefix
sys.exec_prefix         # Platform-specific prefix
sys.executable          # Python interpreter path

# Arguments
sys.argv                # CLI args (list[str])
sys.flags               # Interpreter flags

# I/O
sys.stdin               # TextIOWrapper
sys.stdout
sys.stderr
sys.stdin.buffer        # Binary
sys.stdout.buffer
sys.stderr.buffer

# Exit
sys.exit(code)          # SystemExit
sys.exit("message")     # Prints to stderr, exit 1

# Modules
sys.modules             # Loaded modules dict
sys.builtin_module_names
```

### Platform Detection
```python
import sys, os

sys.platform            # "linux", "darwin", "win32", "cygwin"
os.name                 # "posix", "nt", "java"

# Better: platform module
import platform
platform.system()       # "Linux", "Darwin", "Windows"
platform.release()      # Kernel version
platform.machine()      # "x86_64", "arm64"
platform.python_implementation()  # "CPython", "PyPy"
```

---

## Decision Rules

| Need | Module | Function |
|------|--------|----------|
| Env vars | `os` | `os.getenv`, `os.environ` |
| CWD | `os` | `os.getcwd`, `os.chdir` |
| CLI args | `sys` | `sys.argv` |
| Python version | `sys` | `sys.version_info` |
| Module path | `sys` | `sys.path` |
| Std I/O | `sys` | `sys.std*` |
| Exit | `sys` | `sys.exit` |
| Random bytes | `os` | `os.urandom` |
| Platform | `platform` | `platform.system()` |

---

## Preferred Patterns

```python
# Environment-based config
def get_config() -> Config:
    return Config(
        database_url=os.getenv("DATABASE_URL", "sqlite:///local.db"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        port=int(os.getenv("PORT", "8000")),
    )

# Platform-specific paths
def get_data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:  # Linux/Unix
        base = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "myapp"

# Safe subprocess with clean env
def run_clean(cmd: list[str]):
    clean_env = {
        "PATH": "/usr/bin:/bin",
        "LANG": "C.UTF-8",
        "HOME": "/tmp",
    }
    return subprocess.run(cmd, env=clean_env, ...)
```

---

## Avoid

- `os.path` for new code (use `pathlib`)
- `os.system`, `os.popen` (use `subprocess`)
- Modifying `sys.path` at runtime (use proper packaging)
- `sys.exit()` in library code (raise exceptions)
- Hardcoding paths (`/tmp`, `C:\\Temp`)
- Assuming Unix paths on Windows

---

## Validation Considerations

- Test on target platforms (Windows vs Unix)
- Verify env var handling with missing/empty values
- Check path handling with spaces, unicode

---

## Related Skills

- `stdlib/pathlib.md`
- `stdlib/subprocess.md`
- `engineering/configuration.md`
- `engineering/virtual_environments.md`
- `security/secrets.md`