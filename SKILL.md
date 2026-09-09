# Python Skills System

**Role**: Expert Python software engineer for AI coding agents.

**Scope**: Python code generation, modification, debugging, review, refactoring, testing, and project engineering.

---

## Priority Order

```
Correctness
↓
Security
↓
Preservation of intended behavior
↓
Maintainability
↓
Readability
↓
Appropriate performance
↓
Pythonic style
```

Do not sacrifice correctness for cleverness.
Do not optimize prematurely.
Do not introduce unnecessary complexity.

---

## Code Generation Workflow

```
UNDERSTAND
→ INSPECT
→ PLAN
→ SELECT RELEVANT SKILLS
→ IMPLEMENT
→ REVIEW
→ VALIDATE
→ FIX
→ FINALIZE
```

### Before modifying existing code, INSPECT:

- Python version (`pyproject.toml`, CI, Dockerfile, docs)
- Project structure and package layout
- `pyproject.toml` (dependencies, tooling, config)
- Existing dependencies and their versions
- Existing abstractions, utilities, patterns
- Existing test structure and conventions
- Related modules and their interfaces
- Configuration management approach
- Error-handling conventions
- Logging setup

**Rule**: Do not invent a new architecture when an existing project already has an appropriate one.

---

## Existing-Code Rules (Critical)

When modifying an existing codebase:

- Preserve existing behavior outside the requested scope
- Follow existing project conventions where reasonable
- Reuse existing utilities and abstractions when appropriate
- Avoid duplicate functionality
- Avoid unnecessary file creation
- Avoid unnecessary dependency changes
- Avoid unrelated refactoring
- Make the smallest coherent change that satisfies the requirement
- Do not silently change public APIs
- Do not silently change data formats
- Do not silently change error behavior unless required
- Check related tests before changing behavior

**Integration with the existing codebase is more important than producing an isolated "perfect" implementation.**

---

## Skill Loading Architecture (Optimized)

The agent uses **progressive loading** - only loads what's needed for the task.

### Level 0: Always Loaded (Core Policies)

These policies apply to EVERY task. Load the condensed summary below.

| Policy | Summary |
|--------|---------|
| **Workflow** | UNDERSTAND → INSPECT → PLAN → SELECT → IMPLEMENT → REVIEW → VALIDATE → FIX → FINALIZE |
| **Error Handling** | Catch specific exceptions; chain with `from e`; never bare `except:`; use custom exceptions for domain errors |
| **Type Hints** | Use built-in generics (3.9+); `str \| None` not `Optional[str]`; `Protocol` for interfaces; avoid `Any` |
| **Validation** | Syntax → Type check → Lint → Tests → Execution; never claim "tested"/"verified" without evidence |
| **Naming** | PEP 8: `snake_case` functions, `PascalCase` classes, `UPPER_SNAKE` constants; descriptive not abbreviated |
| **Readability** | Guard clauses; <30 lines/functions; <4 params; blank lines between logical sections |
| **Functions** | Single responsibility; early returns; pure functions where possible; config objects for >4 params |
| **Anti-Patterns** | No bare `except`; no mutable defaults; no globals; no premature async/optimization; no hardcoded secrets |
| **Input Validation** | Validate at boundaries; allowlist not blocklist; size limits; sanitize on output |
| **Secrets** | Environment variables only; never hardcode; sanitize in logs; rotate keys |

---

### Level 0: Always Loaded (Condensed - ~3KB)

The following are ALWAYS active for every task:

1. **Workflow** (condensed): `generation/workflow.md` summary above
2. **Error Handling** (condensed): `generation/error_handling.md` summary above
3. **Type Hints** (condensed): `generation/type_hints.md` summary above
4. **Validation Pipeline** (condensed): `generation/validation_pipeline.md` summary above
5. **Naming**: `quality/naming.md` summary above
6. **Readability**: `quality/readability.md` summary above
7. **Functions**: `quality/functions.md` summary above
8. **Anti-Patterns**: `anti_patterns/index.md` summary above
9. **Input Validation**: `security/input_validation.md` summary above
10. **Secrets**: `security/secrets.md` summary above

**Load these summaries first. Full files only if needed.**

---

## Skill Loading Router

### Step 1: Classify Task

Extract keywords → determine primary task class:

| Class | Keywords |
|-------|----------|
| `generate` | create, new, implement, build, generate, scaffold |
| `modify` | fix, update, change, modify, refactor, add feature, patch |
| `debug` | debug, bug, error, crash, fail, trace, investigate, root cause |
| `test` | test, testing, pytest, unit test, integration test, coverage |
| `review` | review, audit, evaluate, assess, check quality |
| `review_security` | security, vulnerability, audit, exploit, injection, traverse, XSS, CSRF |

**Single primary class per task** (use most specific match).

---

### Step 2: Select Level 1 Primary Skill

| Task Class | Primary Skill (Level 1) |
|------------|-------------------------|
| `generate` (new module) | `engineering/project_structure.md` |
| `generate` (function) | `core/functions.md` |
| `generate` (data) | `stdlib/collections.md` |
| `generate` (CLI) | `engineering/cli_apps.md` |
| `generate` (HTTP) | `engineering/http_clients.md` |
| `generate` (database) | `engineering/database.md` |
| `generate` (async) | `generation/async_concurrency.md` |
| `modify` | `generation/workflow.md` + `generation/error_handling.md` |
| `debug` | `debugging/root_cause.md` |
| `test` | `testing/pytest.md` |
| `review` | `quality/readability.md` |
| `review_security` | `security/input_validation.md` |

**Rule**: Exactly ONE primary skill per task.

---

### Step 3: Evaluate Level 2 Supporting Skills (Conditional)

Load ONLY if condition met:

| Condition | Supporting Skills (Level 2) |
|-----------|----------------------------|
| HTTP task | `engineering/http_clients.md` |
| Database task | `engineering/database.md` + `security/sql_injection.md` |
| CLI task | `engineering/cli_apps.md` + `stdlib/argparse.md` |
| Async task | `generation/async_concurrency.md` |
| Filesystem I/O | `stdlib/pathlib.md` + `security/path_traversal.md` |
| Subprocess | `stdlib/subprocess.md` + `security/command_injection.md` |
| Serialization | `stdlib/json.md` + `security/unsafe_deserialization.md` |
| Secrets/Env vars | `security/secrets.md` |
| Auth/Authorization | `security/auth_boundaries.md` |
| Subprocess usage | `stdlib/subprocess.md` + `security/command_injection.md` |
| Packaging/Release | `engineering/packaging.md` |
| Configuration | `engineering/configuration.md` |
| Testing | `testing/pytest.md` |
| Refactoring | `refactoring/safe_refactoring.md` |
| Security audit | `security/*` (all) |

**Rule**: Load supporting skill ONLY if condition met.

---

### Step 4: Validation Skills (Conditional)

| Trigger | Validation Skills (Level 3) |
|---------|----------------------------|
| Any code generation | `generation/validation_pipeline.md` |
| Type annotations | `quality/type_annotations.md` + `generation/protocols_generics.md` |
| Security code | `security/*` + `generation/validation_pipeline.md` |
| Refactoring | `testing/regression_tests.md` + `refactoring/behavior_preservation.md` |
| Debugging | `debugging/root_cause.md` + `testing/regression_tests.md` |
| New module/package | `engineering/pyproject_toml.md` + `engineering/packaging.md` |

---

### Step 4: Deep References (On-Demand Only)

**NEVER load unless explicitly needed:**

`core/variables_types.md`, `core/control_flow.md`, `core/advanced_python.md`, `core/comprehensions.md`, `core/oop.md`, `core/data_structures.md`, `stdlib/collections.md`, `stdlib/itertools.md`, `stdlib/functools.md`, `stdlib/datetime.md`, `stdlib/re.md`, `stdlib/subprocess.md`, `engineering/pyproject_toml.md`, `engineering/packaging.md`, `engineering/virtual_environments.md`, `quality/abstractions.md`, `quality/duplication.md`, `quality/comments.md`, `quality/documentation.md`, `refactoring/incremental.md`, `refactoring/interface_stability.md`, `debugging/common_bugs.md`, `debugging/inspection_techniques.md`

---

## Skill Loading Algorithm

```
1. Parse task → extract keywords
2. Classify task → determine primary class (generate/modify/debug/test/review/security)
3. Load Level 0 summaries (always)
4. Select ONE Level 1 primary skill from routing table
5. Evaluate Level 2 conditions → load supporting if condition met
6. Evaluate Level 3 conditions → load validation if applicable
6. NEVER load Level 4 unless explicitly requested
7. Resolve dependencies (if skill A requires B, load both)
```

---

## Dependency Graph (Key Relationships)

```
engineering/database.md
    ↓ requires
security/sql_injection.md

engineering/http_clients.md
    ↓ requires
generation/error_handling.md
    ↓ requires
testing/pytest.md

engineering/cli_apps.md
    ↓ requires
stdlib/argparse.md
    ↓ requires
engineering/configuration.md

generation/async_concurrency.md
    ↓ requires
generation/error_handling.md
    ↓ requires
testing/async_tests.md

security/input_validation.md
    ↓ requires
generation/error_handling.md
    ↓ requires
security/secrets.md

refactoring/safe_refactoring.md
    ↓ requires
refactoring/behavior_preservation.md
    ↓ requires
testing/regression_tests.md
```

---

## Task → Skill Mapping (Quick Reference)

| Task | Level 1 | Level 2 | Level 3 | Level 4 (On-Demand) |
|------|---------|---------|---------|---------------------|
| Simple function | `core/functions.md` | — | `validation_pipeline.md` | `core/control_flow.md` |
| HTTP mod | `engineering/http_clients.md` | `error_handling.md`, `secrets.md`, `input_validation.md` | `validation_pipeline.md` | `stdlib/subprocess.md` |
| SQLite | `engineering/database.md` | `sql_injection.md`, `error_handling.md` | `validation_pipeline.md`, `pytest.md` | `stdlib/sqlite3.md` |
| Async debug | `debugging/root_cause.md` | `async_concurrency.md`, `error_handling.md` | `async_tests.md`, `regression_tests.md` | `inspection_techniques.md` |
| CLI | `engineering/cli_apps.md` | `argparse.md`, `configuration.md`, `secrets.md` | `validation_pipeline.md`, `pytest.md` | `packaging.md` |
| Security review | `security/input_validation.md` | `security/*` | `validation_pipeline.md` | `auth_boundaries.md` |
| Refactoring | `refactoring/safe_refactoring.md` | `behavior_preservation.md`, `abstractions.md` | `regression_tests.md`, `validation_pipeline.md` | `incremental.md`, `interface_stability.md` |
| Code review | `quality/readability.md` | `maintainability.md`, `functions.md` | `validation_pipeline.md` | `abstractions.md`, `documentation.md` |

---

## Skill Metadata (Frontmatter)

Each skill file SHOULD have this YAML frontmatter:

```yaml
---
name: skill_name
purpose: One-line description
category: core|stdlib|generation|engineering|quality|security|testing|refactoring|debugging|anti_patterns
triggers:
  - keyword1
  - keyword2
dependencies:
  - skill_name1
  - skill_name2
priority: always|primary|supporting|validation|deep
estimated_tokens: 1500
---
```

---

## Skill Directory Structure (Reference)

```
python-skills/
├── SKILL.md                    # This file - entry point + router
├── ROUTER.md                   # Detailed routing architecture
├── core/                       # Core Python language knowledge
├── stdlib/                     # Standard library focused skills
├── generation/                 # Code generation rules
├── engineering/                # Project engineering
├── quality/                    # Code quality rules
├── security/                   # Security integrated into generation
├── testing/                    # Testing system
├── refactoring/                # Refactoring rules
├── debugging/                  # Debugging guidance
└── anti_patterns/              # Anti-pattern prevention
```

---

## Research Sources (Authoritative)

1. **Python Official Documentation** (docs.python.org)
2. **PEPs**: 8 (Style), 20 (Zen), 257 (Docstrings), 3101 (Formatting), 484/585/604/612/646/673/675/695 (Typing), 626 (Debugging), 654 (Exception Groups), 695 (Type Parameters), 701 (Syntax Formalization), 709 (Comprehension Inlining)
3. **Python Packaging User Guide** (packaging.python.org)
4. **PyPA specifications** (pyproject.toml, lock files, metadata)
5. **Tool documentation**: pytest, mypy, ruff, black, hatch, poetry, uv, tox
6. **CPython source** for standard library behavior
7. **Typing specs**: typing-extensions, typing spec

---

## Validation Requirements

The agent must **never claim** without evidence:
- "tested" — only after running tests
- "verified" — only after validation pipeline
- "linted" — only after linter runs clean
- "type-safe" — only after type checker passes
- "production-ready" — only after full validation
- "fixed" — only after reproduction + fix + regression test

---

## Python Version Policy

- Determine target version from project evidence (`pyproject.toml`, CI, Dockerfile, docs)
- Do not assume newest Python version
- Do not use version-specific syntax/features unless compatible
- Respect project's existing type-checking configuration

---

## Anti-Pattern Prevention (Always Active)

The agent must actively avoid generating:

- Bare `except:` / `except Exception:`
- Mutable default arguments
- Unnecessary global state
- Swallowed exceptions
- Unnecessary dependencies
- Excessive inheritance
- Premature abstraction
- Giant functions (>50 lines)
- God classes
- Duplicated logic
- Clever unreadable one-liners
- Unnecessary comprehensions
- Premature async
- Premature optimization
- Hardcoded secrets
- Unsafe subprocess usage
- Unsafe deserialization (pickle, yaml.load)
- SQL injection vulnerabilities
- Insecure temporary file handling
- Unnecessary `eval` / `exec`

---

## Self-Review Checklist (Before Delivering Code)

- [ ] Correctness: Does it solve the stated problem?
- [ ] Security: No injection, secrets, unsafe deserialization?
- [ ] Behavior preservation: Existing tests pass? No silent API changes?
- [ ] Maintainability: Clear structure, reasonable coupling?
- [ ] Readability: Meaningful names, clear flow?
- [ ] Type hints: Appropriate, not excessive?
- [ ] Tests: Existing + new tests considered?
- [ ] Dependencies: Stdlib first, existing deps second, justified new deps?
- [ ] Python version: Compatible with target?
- [ ] Validation: Syntax → Type check → Lint → Tests → Execution?