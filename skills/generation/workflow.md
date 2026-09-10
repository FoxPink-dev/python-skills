---
name: workflow
purpose: Explicit code generation workflow for AI agents.
category: generation
triggers:
  - workflow
  - pipeline
  - step
  - stage
  - orchestration
dependencies: []
related: []
priority: primary
estimated_tokens: 1226
---
# Generation: Workflow

**Purpose**: Explicit code generation workflow for AI agents.

**When to use**: Every code generation or modification task.
---
---
name: generation_workflow
purpose: Explicit code generation workflow for AI agents
category: generation
triggers:
  - workflow
  - implementation
  - code generation
  - modification
  - validation
  - review
dependencies:
  - core/* (all core language skills)
  - generation/type_hints.md
  - generation/error_handling.md
  - generation/validation_pipeline.md
  - engineering/pyproject_toml.md
  - testing/organization.md
  - security/*
priority: primary
estimated_tokens: 2000
---

## Workflow Steps

### 1. UNDERSTAND
- What is the user asking for?
- What problem does this solve?
- What are the constraints (performance, compatibility, security)?
- What is the expected output (function, class, module, fix)?

### 2. INSPECT (Existing Codebase)
Before touching code, gather:
- Python version (`pyproject.toml`, CI, Dockerfile, docs)
- Project structure and package layout
- `pyproject.toml` (dependencies, tooling, config)
- Existing dependencies and versions
- Existing abstractions, utilities, patterns
- Existing test structure and conventions
- Related modules and their interfaces
- Configuration management approach
- Error-handling conventions
- Logging setup

**Do not generate code before inspecting.**

### 3. PLAN
- What files need to change?
- What new code is needed?
- Which existing utilities can be reused?
- What tests need updating?
- What are the integration points?
- What could break?

### 4. SELECT RELEVANT SKILLS
Load skills based on task type (see SKILL.md loading strategy):
- Task-specific skills (HTTP, CLI, DB, etc.)
- Always: `generation/error_handling`, `generation/type_hints`, `quality/naming`
- Security: `security/input_validation`, `security/secrets`
- Testing: `testing/organization`, `testing/fixtures_mocks`

### 5. IMPLEMENT
- Write code following project conventions
- Use existing patterns and utilities
- Add type hints appropriate to project config
- Keep functions small and focused
- Handle errors explicitly
- No premature optimization

### 6. REVIEW
- Does it solve the stated problem?
- Does it preserve existing behavior?
- Are types correct?
- Are errors handled?
- Is it secure?
- Is it readable?
- Are names meaningful?

### 7. VALIDATE
Run project's validation pipeline (detect first):
```bash
# Syntax
python -m py_compile file.py

# Type checking (if configured)
mypy file.py
# or
pyright file.py

# Linting (if configured)
ruff check file.py
# or
flake8 file.py

# Formatting (if configured)
ruff format file.py
# or
black file.py

# Tests
pytest path/to/tests -v
# or project's test command
```

### 8. FIX
- Address all validation failures
- Re-run validation until clean
- Do not skip steps

### 9. FINALIZE
- Confirm all tests pass
- Confirm no regressions
- Document any behavior changes
- Update related documentation if needed

---

## Validation Pipeline (Project-Dependent)

Detect project tooling first:
```bash
# Check for config files
ls pyproject.toml setup.cfg tox.ini ruff.toml .pre-commit-config.yaml
```

| Tool | Command | Purpose |
|------|---------|---------|
| mypy | `mypy .` | Static type checking |
| pyright | `pyright` | Fast type checking |
| ruff | `ruff check .` | Linting (fast) |
| black | `black --check .` | Formatting check |
| pytest | `pytest` | Testing |
| bandit | `bandit -r .` | Security linting |

**Never claim** "tested", "verified", "linted", "type-safe" without running the tools.

---

## Existing Code Modification Rules

When modifying existing code:

1. **Understand first** — read related files, understand the flow
2. **Minimal change** — smallest coherent change
3. **Preserve behavior** — existing tests must pass
4. **Follow conventions** — match existing style, patterns
5. **Reuse** — use existing utilities, don't duplicate
6. **Test** — run related tests before and after

---

## Integration Over Perfection

**The agent should understand that integration with the existing codebase is more important than producing an isolated "perfect" implementation.**

- Match the project's architecture
- Use the project's utilities
- Follow the project's error handling
- Respect the project's type hint level
- Keep the project's test patterns

---

## Decision Checklist (Before Generating)

- [ ] Inspected project structure and conventions
- [ ] Identified relevant existing code
- [ ] Selected appropriate skills
- [ ] Planned minimal coherent change
- [ ] Know how to validate (test command, lint, type check)
- [ ] Considered security implications
- [ ] Considered Python version compatibility

---

## Related Skills

- `core/*` (all core language skills)
- `generation/type_hints.md`
- `generation/error_handling.md`
- `generation/validation_pipeline.md`
- `engineering/pyproject_toml.md`
- `testing/organization.md`
- `security/*`