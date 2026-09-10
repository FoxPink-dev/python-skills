---
name: subprocess
purpose: Safe subprocess execution and process management.
category: stdlib
triggers:
  - subprocess
  - run
  - popen
  - shell
  - pipe
  - timeout
dependencies: []
related: []
priority: supporting
estimated_tokens: 1262
---
# Stdlib: subprocess

**Purpose**: Safe subprocess execution and process management.

**When to use**: Running external commands. Prefer stdlib APIs when possible.

---

## Core Rules

### Basic Usage (Python 3.5+)
```python
import subprocess
from pathlib import Path

# Simple run (recommended)
result = subprocess.run(
    ["cmd", "arg1", "arg2"],
    capture_output=True,  # stdout, stderr as bytes
    text=True,            # Decode as str (encoding=locale)
    encoding="utf-8",     # Explicit encoding
    timeout=30,           # Seconds
    check=False,          # Don't raise on non-zero
    cwd=Path("/work"),
    env={"VAR": "value"}, # Or None to inherit
)

result.returncode
result.stdout
result.stderr
```

### Safe Patterns
```python
# ALWAYS use list form (not shell=True)
subprocess.run(["git", "status"])  # Safe
subprocess.run("git status", shell=True)  # UNSAFE - shell injection!

# With input
result = subprocess.run(
    ["grep", "pattern"],
    input="data\nto\nsearch",
    capture_output=True,
    text=True,
)

# Streaming (large output)
proc = subprocess.Popen(
    ["cmd", "arg"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)
for line in proc.stdout:
    process(line)
proc.wait()
```

### Error Handling
```python
try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    # e.returncode, e.stdout, e.stderr, e.cmd
    logger.error("Command failed", extra={"cmd": e.cmd, "stderr": e.stderr})
    raise
except subprocess.TimeoutExpired as e:
    # e.stdout, e.stderr (partial)
    logger.error("Command timed out")
    raise
except FileNotFoundError:
    logger.error("Command not found", extra={"cmd": cmd[0]})
    raise
```

### Pipes and Chaining
```python
# Safe pipeline without shell
p1 = subprocess.Popen(["cmd1"], stdout=subprocess.PIPE)
p2 = subprocess.Popen(["cmd2"], stdin=p1.stdout, stdout=subprocess.PIPE)
p1.stdout.close()  # Allow p1 to receive SIGPIPE
output = p2.communicate()[0]
```

### Environment
```python
# Inherit + modify
env = os.environ.copy()
env["CUSTOM_VAR"] = "value"
subprocess.run(cmd, env=env)

# Clean environment
subprocess.run(cmd, env={"PATH": "/usr/bin", "HOME": "/tmp"})
```

---

## Security Rules (Critical)

### NEVER use `shell=True` with untrusted input
```python
# DANGEROUS
subprocess.run(f"echo {user_input}", shell=True)
# User input: "; rm -rf /"

# SAFE
subprocess.run(["echo", user_input])
```

### Validate/Allowlist Commands
```python
ALLOWED_COMMANDS = {"git", "docker", "kubectl"}

def safe_run(cmd: list[str], **kwargs):
    if cmd[0] not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {cmd[0]}")
    return subprocess.run(cmd, **kwargs)
```

### Path Safety
```python
# Resolve paths, prevent traversal
safe_path = Path(user_input).resolve()
if not safe_path.is_relative_to(ALLOWED_ROOT):
    raise ValueError("Path traversal attempt")
subprocess.run(["process", str(safe_path)])
```

---

## Decision Rules

| Situation | Approach |
|-----------|----------|
| Simple command, wait for result | `subprocess.run()` |
| Need streaming/large output | `subprocess.Popen` |
| Pipeline | `Popen` chain (no shell) |
| Fire and forget | `Popen` + `detach()` or `start_new_session=True` |
| Need shell features (glob, vars) | Avoid; reimplement in Python |
| Untrusted input in command | List form, validate/allowlist |

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
) -> subprocess.CompletedProcess:
    """Safe subprocess wrapper."""
    # Validate command
    if not cmd or not isinstance(cmd, list):
        raise ValueError("Command must be non-empty list")
    
    # Allowlist check (optional but recommended)
    # if cmd[0] not in ALLOWED_COMMANDS: ...
    
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",  # Handle encoding issues
        timeout=timeout,
        check=False,       # Handle returncode manually
        cwd=cwd,
        env=env,
        input=input_data,
    )

# Usage
result = run_command(["git", "diff", "--name-only"])
if result.returncode != 0:
    logger.warning("Git diff failed", stderr=result.stderr)
files = result.stdout.strip().splitlines()
```

---

## Avoid

- `shell=True` (except trusted, static commands)
- String commands (always use list)
- Unvalidated user input in command args
- `os.system()`, `os.popen()` (legacy, unsafe)
- Ignoring `returncode`
- No timeout (hangs indefinitely)
- Inheriting env without consideration (leaks secrets)

---

## Validation Considerations

- Test with malicious input (injection attempts)
- Verify timeout behavior
- Check encoding handling
- Audit command allowlists

---

## Related Skills

- `security/command_injection.md`
- `security/path_traversal.md`
- `stdlib/os_sys.md`
- `engineering/configuration.md`