# Python Skills

Python engineering skills for AI coding agents.

## Overview

Python Skills is a comprehensive knowledge base of 69 skills across 10 categories, designed to help AI coding agents write better Python code.

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
# Check status
python -m python_skills status

# Install for specific targets
python -m python_skills install --target claude --target cursor

# Sync with latest skills
python -m python_skills sync

# Check status
python -m python_skills status
```

## Target Environments

- **Claude Code**: Native skills in `.claude/skills/`, rules in `.claude/rules/`
- **Cursor**: Rules in `.cursor/rules/`
- **Kiro**: Skills in `.kiro/skills/`, steering in `.kiro/steering/`
- **Cline**: Rules in `.clinerules/`
- **Universal**: `AGENTS.md` bootstrap

## License

MIT License