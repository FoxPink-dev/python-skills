---
name: dependency_risks
purpose: Manage security risks from third-party dependencies.
category: security
triggers:
  - dependency
  - supply-chain
  - vulnerability
  - sca
  - audit
  - cve
dependencies: []
related: []
priority: critical
estimated_tokens: 1340
---
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

### SBOM Generation (Software Bill of Materials)
```bash
# SPDX SBOM (cyclonedx-python)
pip install cyclonedx-bom
cyclonedx-py -i -o sbom.json --format json

# Or with pip-licenses
pip install pip-licenses
pip-licenses --format=json --output-file=licenses.json

# Syft (supports multiple formats)
syft packages dir:. -o spdx-json=sbom.spdx.json
syft packages dir:. -o cyclonedx-json=sbom.cdx.json

# In CI
- name: Generate SBOM
  run: |
    syft packages dir:. -o cyclonedx-json=sbom.cdx.json
  if: always()
```

### VEX (Vulnerability Exploitability eXchange)
```json
{
  "@context": "https://openvex.dev/ns/openvex-1.0.0.json",
  "@id": "https://example.com/vex/123",
  "author": "Acme Corp",
  "role": "manufacturer",
  "timestamp": "2024-01-15T10:00:00Z",
  "version": 1,
  "statements": [
    {
      "vulnerability": {
        "name": "CVE-2024-1234",
        "description": "Buffer overflow in libfoo"
      },
      "products": [
        {
          "@id": "pkg:pypi/requests@2.31.0",
          "subcomponents": []
        }
      ],
      "status": "not_affected",
      "justification": "vulnerable_code_not_in_execute_path",
      "impact_statement": "The vulnerable function is never called in our codebase"
    }
  ]
}
```

```bash
# Generate VEX with vexctl
vexctl create --cve CVE-2024-1234 --status not_affected \
  --justification vulnerable_code_not_in_execute_path \
  --product "pkg:pypi/requests@2.31.0" \
  --output vex.json
```

### License Compliance Automation
```bash
# pip-licenses for license audit
pip install pip-licenses
pip-licenses --format=json --output-file=licenses.json

# Check for incompatible licenses
pip-licenses --from=mixed --with-urls --no-license-path \
  --ignore-packages="pkg1,pkg2" \
  --fail-on="GPL-3.0,AGPL-3.0"

# In CI - fail on copyleft
- name: License Check
  run: |
    pip-licenses --format=plain-vertical \
      --fail-on="GPL-3.0,AGPL-3.0,LGPL-3.0"
```

```python
# Python: Automated license check
import subprocess
import json
from pathlib import Path

ALLOWED_LICENSES = {
    "MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0",
    "PSF-2.0", "ISC", "MPL-2.0", "Python-2.0"
}

DISALLOWED_LICENSES = {"GPL-3.0", "AGPL-3.0", "LGPL-3.0"}

def check_licenses() -> tuple[bool, list[str]]:
    """Check all dependencies for license compliance."""
    result = subprocess.run(
        ["pip-licenses", "--format=json"],
        capture_output=True, text=True
    )
    violations = []
    for dep in json.loads(result.stdout):
        license_name = dep.get("License", "Unknown")
        if license_name in DISALLOWED_LICENSES:
            violations.append(f"{dep['Name']}: {license_name}")
        elif license_name not in ALLOWED_LICENSES and license_name != "Unknown":
            violations.append(f"{dep['Name']}: {license_name} (review needed)")
    return len(violations) == 0, violations
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

### Production Gotchas

| Gotcha | Symptom | Fix |
|--------|---------|-----|
| No SBOM | Can't respond to supply chain incidents | Generate SBOM on every release |
| No VEX | False positives block deployments | Document why CVE doesn't affect you |
| License drift | Copyleft dep added unnoticed | `pip-licenses --fail-on` in CI |
| Transitive vulns | Direct deps clean but transitive vulnerable | Scan full dependency tree |
| Hash mismatch | Supply chain attack (compromised PyPI) | `pip install --require-hashes` |
| Unmaintained dep | No security updates for years | Track "last release" date, plan replacement |
| Private index leak | Internal packages on public index | Separate indexes, strict access control |

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