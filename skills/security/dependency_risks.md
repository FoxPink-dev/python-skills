# Security: Dependency Risks

**Purpose**: Manage security risks from third-party dependencies.

**When to use**: Adding dependencies, updating, CI/CD pipeline.

## Core Rules

### Dependency Evaluation Checklist
Before adding a dependency:
- [ ] **Necessary?** Stdlib or existing dep can't solve it
- [ ] **Maintained?** Recent releases, open issues responded to
- [ ] **Popular?** Sufficient usage (downloads, dependents)
- [ ] **License?** Compatible with project
- [ ] **Security history?** No unpatched vulnerabilities
- [ ] **Transitive deps?** Minimal, well-known
- [ ] **Size?** Reasonable install footprint

### Scanning Tools
```bash
# Safety (PyPI vulnerability database)
pip install safety
safety check
safety check --json

# pip-audit (uses OSV database)
pip install pip-audit
pip-audit
pip-audit --desc

# GitHub Dependabot / GitLab Dependency Scanning
# Configure in CI/CD

# OWASP Dependency Check
# For comprehensive scanning
```

### Lock File Security
```bash
# Generate with hashes (pip-tools)
pip-compile --generate-hashes pyproject.toml -o requirements.txt

# Verify on install
pip install --require-hashes -r requirements.txt

# uv (includes hashes by default)
uv pip compile pyproject.toml -o requirements.txt
uv sync  # Verifies hashes
```

### Update Policy
```bash
# Check outdated
uv pip list --outdated
pip list --outdated

# Security updates: IMMEDIATE
# Patch/feature updates: Scheduled (weekly/monthly)

# Test before deploying updates
uv pip install --upgrade package
pytest  # Full suite
```

### Private Package Index
```bash
# Use private index for internal packages
pip install --index-url https://private.pypi.org/simple my-package

# Or in pyproject.toml
[tool.uv]
index-url = "https://private.pypi.org/simple"
```

### Supply Chain Security
```toml
# pyproject.toml - require hashes for production deps
[project]
dependencies = [
    "requests==2.31.0 --hash=sha256:...",
]

# Or use pip-tools with --generate-hashes
```

---

## Decision Rules

| Risk Level | Action |
|------------|--------|
| Critical vulnerability | Update immediately, emergency deploy |
| High vulnerability | Update within 24-48 hours |
| Medium vulnerability | Update within week |
| Low vulnerability | Next scheduled update |
| Unmaintained dependency | Plan replacement |
| License conflict | Replace immediately |

---

## Preferred Patterns

```bash
# CI Pipeline
# 1. Scan on every PR
safety check --json
pip-audit --desc

# 2. Scheduled scan (daily/weekly)
# GitHub Actions cron / GitLab scheduled pipeline

# 3. Automated PR for updates
# dependabot.yml / renovate.json

# 4. Block merge on critical vulns
# Required status check
```

### dependabot.yml Example
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    labels:
      - "dependencies"
      - "security"
    allow:
      - dependency-type: "direct"
    ignore:
      - dependency-name: "some-package"
        versions: [">=2.0.0"]
```

### renovate.json Example
```json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchUpdateType": "security",
      "automerge": true,
      "schedule": ["after 6pm", "before 9am"]
    }
  ],
  "pip": {
    "file": "requirements.txt"
  }
}
```

### Python Code: Automated Check
```python
import subprocess
import json
from pathlib import Path

def scan_dependencies(requirements_path: Path) -> dict:
    """Run safety and pip-audit, return combined results."""
    results = {"critical": [], "high": [], "medium": [], "low": []}
    
    # Safety
    try:
        proc = subprocess.run(
            ["safety", "check", "--json", "-r", str(requirements_path)],
            capture_output=True, text=True, timeout=60
        )
        if proc.returncode != 0:
            for vuln in json.loads(proc.stdout):
                severity = vuln.get("severity", "unknown").lower()
                if severity in results:
                    results[severity].append(vuln)
    except Exception:
        pass
    
    # pip-audit
    try:
        proc = subprocess.run(
            ["pip-audit", "--desc", "--format", "json", "-r", str(requirements_path)],
            capture_output=True, text=True, timeout=60
        )
        if proc.returncode != 0:
            data = json.loads(proc.stdout)
            for vuln in data.get("vulnerabilities", []):
                severity = vuln.get("severity", "unknown").lower()
                if severity in results:
                    results[severity].append(vuln)
    except Exception:
        pass
    
    return results

def has_critical_vulns(results: dict) -> bool:
    return len(results.get("critical", [])) > 0 or len(results.get("high", [])) > 0
```

---

## Avoid

- No vulnerability scanning
- Pinned exact versions without updates (`==1.0.0` forever)
- No lock file for applications
- Ignoring transitive dependencies
- Using packages with known vulnerabilities
- Installing from untrusted indexes

---

## Validation Considerations

- CI fails on critical/high vulnerabilities
- Lock file hashes verified on install
- SBOM (Software Bill of Materials) generated
- License compliance checked

---

## Related Skills

- `engineering/dependency_management.md`
- `engineering/pyproject_toml.md`
- `engineering/virtual_environments.md`
- `engineering/packaging.md`