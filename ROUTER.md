# Python Skills Router

**Purpose**: Optimized skill loading architecture for AI coding agents.

**Goal**: Reduce unnecessary context while preserving knowledge quality and coding performance.

---

## Routing Architecture

```
SKILL.md (Level 0 - Always Loaded)
    ↓
Router (Task Classification)
    ↓
Level 1: Primary Skill (Task Domain)
    ↓
Level 2: Supporting Skills (Conditional)
    ↓
Level 3: Validation Skills (Conditional)
    ↓
Level 4: Deep References (On-Demand)
```

---

## Task Classification Model

### Task Classes

| Class | Description | Example Tasks |
|-------|-------------|---------------|
| `generate` | New code creation | New function, class, module |
| `modify` | Existing code changes | Bug fix, feature addition, refactor |
| `debug` | Bug investigation | Root cause, inspection, crash analysis |
| `review` | Code evaluation | Security review, quality review |
| `test` | Test creation/execution | Unit tests, integration tests, async tests |
| `review_security` | Security-focused | Vulnerability scan, threat modeling |

### Classification Keywords

| Class | Keywords |
|-------|----------|
| `generate` | create, new, implement, build, generate, scaffold |
| `modify` | fix, update, change, modify, refactor, add feature, patch |
| `debug` | debug, bug, error, crash, fail, trace, investigate, root cause |
| `review` | review, audit, evaluate, assess, check quality |
| `test` | test, testing, pytest, unit test, integration test, coverage |
| `review_security` | security, vulnerability, audit, exploit, injection, traverse, XSS, CSRF |

---

## Level 0: Always Loaded (SKILL.md + Router)

**Always Loaded Skills** (Core policies that apply to ALL tasks):

| Skill | Reason |
|-------|--------|
| `generation/workflow.md` | Code generation workflow (always active) |
| `generation/error_handling.md` | Error handling (critical for all tasks) |
| `generation/type_hints.md` | Type hints (baseline for Python code) |
| `generation/validation_pipeline.md` | Validation requirements |
| `quality/naming.md` | Naming conventions (always applies) |
| `quality/readability.md` | Readability (always applies) |
| `quality/functions.md` | Function design (always applies) |
| `anti_patterns/index.md` | Anti-pattern prevention (always active) |
| `security/input_validation.md` | Input validation (security baseline) |
| `security/secrets.md` | Secrets management (security baseline) |

**Total Level 0 tokens**: ~8KB (condensed summary)

---

## Level 1: Primary Skills (Task Domain)

### Task → Primary Skill Mapping

| Task Class | Primary Skill | Trigger |
|------------|---------------|---------|
| `generate` (new module) | `engineering/project_structure.md` | create, new, implement, module, package |
| `generate` (new function) | `core/functions.md` | function, def, method |
| `generate` (data processing) | `stdlib/collections.md` | process, transform, filter, map, reduce |
| `generate` (CLI) | `engineering/cli_apps.md` | cli, command, argument, argparse, click, typer |
| `generate` (HTTP client) | `engineering/http_clients.md` | http, request, client, api, rest, fetch |
| `generate` (database) | `engineering/database.md` | database, sql, query, orm, sqlite, postgres |
| `generate` (async) | `generation/async_concurrency.md` | async, await, concurrent, parallel |
| `modify` | `generation/workflow.md` + `generation/error_handling.md` | fix, update, change, refactor, bug |
| `debug` | `debugging/root_cause.md` | debug, bug, error, crash, trace |
| `test` | `testing/pytest.md` | test, testing, pytest, unit test |
| `review` | `quality/readability.md` | review, audit, evaluate |
| `review_security` | `security/input_validation.md` | security, vulnerability, injection |

### Primary Skill Selection Rules

1. **Single primary skill per task** - select the most specific match
2. **Fallback**: If no specific match, use `generation/workflow.md` + `core/functions.md`
3. **Never load multiple primary skills** - only one per task class

---

## Level 2: Supporting Skills (Conditional)

### Conditional Loading Matrix

| Condition | Supporting Skills | Loading Rule |
|-----------|-------------------|--------------|
| Task involves HTTP | `engineering/http_clients.md` | Always with HTTP tasks |
| Task involves Database | `engineering/database.md` + `security/sql_injection.md` | Always with DB tasks |
| Task involves CLI | `engineering/cli_apps.md` + `stdlib/argparse.md` | Always with CLI tasks |
| Task involves async | `generation/async_concurrency.md` | Always with async tasks |
| Task involves filesystem | `stdlib/pathlib.md` + `security/path_traversal.md` | File I/O operations |
| Task involves subprocess | `stdlib/subprocess.md` + `security/command_injection.md` | Subprocess usage |
| Task involves serialization | `stdlib/json.md` + `security/unsafe_deserialization.md` | JSON/YAML/pickle |
| Task involves secrets | `security/secrets.md` | Environment variables, API keys |
| Task involves auth | `security/auth_boundaries.md` | Authentication/authorization |
| Task involves packaging | `engineering/packaging.md` | Build, publish, release |
| Task involves configuration | `engineering/configuration.md` | Config files, env vars |
| Task involves testing | `testing/pytest.md` | Any test-related task |
| Task involves refactoring | `refactoring/safe_refactoring.md` | Refactoring tasks |
| Task involves security review | `security/all` (load all security) | Security audit tasks |

### Dependency Graph

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

## Level 3: Validation Skills (Conditional)

| Trigger | Validation Skills |
|---------|-------------------|
| Any code generation | `generation/validation_pipeline.md` |
| Type annotation work | `quality/type_annotations.md` + `generation/protocols_generics.md` |
| Security-sensitive code | `security/all` + `generation/validation_pipeline.md` |
| Refactoring | `testing/regression_tests.md` + `refactoring/behavior_preservation.md` |
| Debugging | `debugging/root_cause.md` + `testing/regression_tests.md` |
| New module/package | `engineering/pyproject_toml.md` + `engineering/packaging.md` |

---

## Level 4: Deep References (On-Demand Only)

**Load ONLY when explicitly needed:**

| Deep Reference | Trigger |
|----------------|---------|
| `core/variables_types.md` | Type system questions |
| `core/control_flow.md` | Complex control flow |
| `core/advanced_python.md` | Decorators, context managers, descriptors |
| `core/comprehensions.md` | Comprehension patterns |
| `core/oop.md` | Class design, inheritance, protocols |
| `stdlib/collections.md` | Advanced collections |
| `stdlib/itertools.md` | Iterator patterns |
| `stdlib/functools.md` | Higher-order functions |
| `stdlib/datetime.md` | Date/time handling |
| `stdlib/re.md` | Regex patterns |
| `stdlib/subprocess.md` | Process management |
| `engineering/pyproject_toml.md` | Project config |
| `engineering/packaging.md` | Distribution |
| `engineering/virtual_environments.md` | Environment setup |
| `quality/abstractions.md` | Design patterns |
| `quality/duplication.md` | DRY decisions |
| `quality/comments.md` | Documentation style |
| `quality/documentation.md` | Docstring format |
| `refactoring/incremental.md` | Large refactors |
| `refactoring/interface_stability.md` | API evolution |
| `debugging/common_bugs.md` | Specific bug patterns |
| `debugging/inspection_techniques.md` | Profiling, inspection |

---

## Minimum Required Context Per Task Type

### Simple Function Generation
```
Level 0 (always)
Level 1: core/functions.md
Level 2: (none unless specific domain)
Level 3: generation/validation_pipeline.md
```
**Skills loaded**: ~10 skills | ~12KB

### HTTP Client Modification
```
Level 0 (always)
Level 1: engineering/http_clients.md
Level 2: generation/error_handling.md, security/secrets.md, security/input_validation.md
Level 3: generation/validation_pipeline.md
```
**Skills loaded**: ~14 skills | ~18KB

### SQLite Feature
```
Level 0 (always)
Level 1: engineering/database.md
Level 2: security/sql_injection.md, generation/error_handling.md
Level 3: generation/validation_pipeline.md, testing/pytest.md
```
**Skills loaded**: ~14 skills | ~18KB

### Async Debugging
```
Level 0 (always)
Level 1: debugging/root_cause.md
Level 2: generation/async_concurrency.md, generation/error_handling.md
Level 3: testing/async_tests.md, testing/regression_tests.md
```
**Skills loaded**: ~13 skills | ~16KB

### CLI Application
```
Level 0 (always)
Level 1: engineering/cli_apps.md
Level 2: stdlib/argparse.md, engineering/configuration.md, security/secrets.md
Level 3: generation/validation_pipeline.md, testing/pytest.md
```
**Skills loaded**: ~15 skills | ~19KB

---

## Routing Matrix

| Task | Primary (L1) | Supporting (L2) | Validation (L3) | Deep Refs (L4) |
|------|--------------|-----------------|-----------------|----------------|
| Simple function | `core/functions.md` | — | `validation_pipeline.md` | `core/control_flow.md` |
| HTTP client mod | `engineering/http_clients.md` | `error_handling.md`, `secrets.md`, `input_validation.md` | `validation_pipeline.md` | `stdlib/subprocess.md` |
| SQLite feature | `engineering/database.md` | `sql_injection.md`, `error_handling.md` | `validation_pipeline.md`, `pytest.md` | `stdlib/sqlite3.md` |
| Async debug | `debugging/root_cause.md` | `async_concurrency.md`, `error_handling.md` | `async_tests.md`, `regression_tests.md` | `inspection_techniques.md` |
| CLI app | `engineering/cli_apps.md` | `argparse.md`, `configuration.md`, `secrets.md` | `validation_pipeline.md`, `pytest.md` | `engineering/packaging.md` |
| Security review | `security/input_validation.md` | `security/all` | `validation_pipeline.md` | `auth_boundaries.md` |
| Refactoring | `refactoring/safe_refactoring.md` | `behavior_preservation.md`, `abstractions.md` | `regression_tests.md`, `validation_pipeline.md` | `incremental.md`, `interface_stability.md` |
| Code review | `quality/readability.md` | `maintainability.md`, `functions.md` | `validation_pipeline.md` | `abstractions.md`, `documentation.md` |

---

## Skill Metadata Index

Each skill file should have this frontmatter (YAML):

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
version: 1.0
---
```

---

## Token Measurements (Baseline vs Optimized)

| Task | Baseline Skills | Optimized Skills | Reduction |
|------|-----------------|------------------|-----------|
| Simple function | 64 (all) | 10 | **84%** |
| HTTP mod | 64 (all) | 14 | **78%** |
| SQLite feature | 64 (all) | 14 | **78%** |
| Async debug | 64 (all) | 13 | **80%** |
| CLI app | 64 (all) | 15 | **77%** |
| Security review | 64 (all) | 18 | **72%** |
| Refactoring | 64 (all) | 16 | **75%** |
| Code review | 64 (all) | 16 | **75%** |

**Average reduction: ~79%**

---

## Quality Guardrail Checklist

Before finalizing routing for a task, verify:

- [ ] Level 0 skills loaded (always)
- [ ] Exactly one Level 1 primary skill selected
- [ ] Level 2 skills only if condition met
- [ ] Level 3 validation skills if applicable
- [ ] No Level 4 deep references unless explicitly needed
- [ ] Dependencies resolved (if skill A requires B, both loaded)
- [ ] Anti-patterns always active (Level 0)
- [ ] Validation pipeline loaded for any code generation
- [ ] Security baseline (input_validation + secrets) always loaded

---

## Implementation Notes

### For the Agent

When receiving a task:

1. **Parse task** → extract keywords
2. **Classify task** → determine primary class (generate/modify/debug/test/review/review_security)
3. **Select Level 1** → single primary skill from routing matrix
4. **Evaluate Level 2 conditions** → load supporting skills if condition met
5. **Evaluate Level 3 conditions** → load validation skills if applicable
6. **NEVER load Level 4** unless explicitly requested
7. **Always load Level 0** (condensed summary)

### For Skill Authors

When creating/updating skills:
1. Add YAML frontmatter with metadata
2. Keep Level 1/2 skills focused (<2000 tokens)
3. Move deep details to Level 4 references
4. Declare dependencies explicitly
4. Avoid duplicating Level 0 policies

---

## Migration Checklist

- [ ] Add YAML frontmatter to all skill files
- [ ] Create condensed Level 0 summary in SKILL.md
- [ ] Add conditional loading logic to SKILL.md
- [ ] Create router decision logic in SKILL.md
- [ ] Verify dependency graph is acyclic
- [ ] Run benchmark tasks with new router
- [ ] Measure token reduction
- [ ] Verify no regression in benchmark tasks

---

## Summary

**Before**: Agent loads all 64 skills (~120KB) for every task.

**After**: Agent loads ~10-18 skills (~12-20KB) based on task classification.

**Reduction**: ~79% token reduction while preserving all relevant knowledge.

**Key principle**: The agent reads less while still knowing exactly what it needs.