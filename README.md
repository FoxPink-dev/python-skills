# Python Skills

Python engineering skills for AI coding agents.

## Overview

Python Skills is a comprehensive knowledge base of 69 skills across 10 categories, designed to help AI coding agents write better Python code. It supports 16 AI coding agents via a unified adapter system.

## Supported Agents

| Agent | Skills Dir | Native Dir | Type |
|-------|-----------|------------|------|
| **OpenCode** | `.agents/skills/` | `.opencode/skills/` | A-NativeSkills |
| **Windsurf** | `.agents/skills/` | `.windsurf/skills/` | A-NativeSkills |
| **VS Code / Copilot** | `.agents/skills/` | `.github/skills/` | A-NativeSkills |
| **Gemini** | `.agents/skills/` | `.gemini/skills/` | A-NativeSkills |
| **Roo Code** | `.agents/skills/` | `.roo/skills/` | A-NativeSkills |
| **Codex** | `.agents/skills/` | — | A-NativeSkills |
| **Goose** | `.agents/skills/` | — | A-NativeSkills |
| **Junie (JetBrains)** | `.agents/skills/` | `.junie/skills/` | A-NativeSkills |
| **Zed** | `.agents/skills/` | — | A-NativeSkills |
| **Continue** | `.continue/rules/` | — | B-NativeRules |
| **Aider** | `PYTHON_SKILLS.md` | `.aider.conf.yml` | D-Config |
| **Claude Code** | `.claude/skills/` | — | A-NativeSkills |
| **Cursor** | `.cursor/rules/` | — | B-NativeRules |
| **Kiro** | `.kiro/skills/` | — | A-NativeSkills |
| **Cline** | `.agents/skills/` | `.clinerules` | A-NativeSkills |
| **Universal** | `AGENTS.md` | — | E-Universal |

## Shared Skills Directory

Targets that support the [Agent Skills specification](https://github.com/opencode-ai/agent-skills) share a single `.agents/skills/` directory. Each target also gets its own vendor-specific directory (e.g., `.opencode/skills/`). Installing multiple targets produces only 67 skill directories, not 67 per target.

## Skill Categories

- **Core**: Python language fundamentals (variables, control flow, functions, data structures, OOP)
- **Stdlib**: Standard library modules (argparse, collections, datetime, functools, itertools, json, logging, pathlib, re, statistics, subprocess)
- **Generation**: Code generation patterns (type hints, protocols, async, error handling, validation, workflow)
- **Engineering**: Production engineering (CLI apps, configuration, databases, HTTP clients, packaging, virtual environments)
- **Quality**: Code quality standards (abstractions, comments, documentation, duplication, functions, maintainability, naming, readability, type annotations)
- **Security**: Security engineering (auth boundaries, command injection, dependency risks, file handling, input validation, path traversal, secrets, SQL injection, unsafe deserialization)
- **Testing**: Testing methodologies (async tests, coverage, edge cases, fixtures/mocks, organization, parameterized, regression tests)
- **Refactoring**: Safe refactoring patterns (behavior preservation, incremental, interface stability, safe refactoring)
- **Debugging**: Debugging techniques (common bugs, inspection, root cause analysis)
- **Anti-patterns**: Anti-pattern prevention

## Installation

```bash
pip install python-skills
```

Or from source:
```bash
git clone https://github.com/FoxPink-dev/python-skills.git
cd python-skills
pip install -e .
```

## Usage

```bash
# Detect available agents
python -m python_skills detect

# Install for all compatible agents
python -m python_skills install --auto

# Install for specific targets
python -m python_skills install --target opencode --target windsurf

# Sync installed skills with latest
python -m python_skills sync

# Check installation status
python -m python_skills status

# Uninstall from all targets
python -m python_skills uninstall --auto
```

## License

MIT License
