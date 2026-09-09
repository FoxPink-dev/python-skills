"""Claude Code adapter for python-skills."""

import os
import shutil
from pathlib import Path
from typing import Optional
from ..adapters.base import AgentAdapter, DetectionResult, InstallResult, SyncResult, UninstallResult, StatusResult
from ..config import Target, Scope
from ..skills.registry import SkillRegistry
from ..state import LockManager


class ClaudeAdapter(AgentAdapter):
    """Adapter for Claude Code."""
    
    name = "Claude Code"
    target = Target.CLAUDE.value
    
    def __init__(self, project_root: Path, skills_registry: SkillRegistry, lock_manager: LockManager, config):
        super().__init__(project_root, skills_registry, lock_manager, config)
    
    def _get_global_path(self) -> Path:
        """Get the global Claude config path."""
        return Path.home() / ".claude"
    
    def detect(self) -> DetectionResult:
        """Detect Claude Code installation and configuration."""
        # Check if claude is in PATH
        app_detected = shutil.which("claude") is not None
        
        # Check for project config
        project_config = (self.project_root / ".claude").exists()
        
        # Check for global config
        global_config = self._get_global_path().exists()
        
        return DetectionResult(
            application_detected=app_detected,
            project_config_detected=project_config,
            adapter_available=True,
            details=f"App: {'yes' if app_detected else 'no'}, Project config: {'yes' if project_config else 'no'}, Global config: {'yes' if global_config else 'no'}"
        )
    
    def install(self, scope: str = "project", dry_run: bool = False) -> InstallResult:
        """Install python-skills for Claude Code."""
        result = InstallResult(success=True, target=self.target, scope=scope)
        target_path = self._get_scope_path(scope)
        
        try:
            # 1. Install native skills to .claude/skills/
            skills_dir = target_path / ".claude" / "skills"
            skills_created = self._install_skills(skills_dir, dry_run)
            result.files_created.extend(skills_created)
            
            # 2. Generate path-scoped rules
            rules_created = self._install_rules(target_path, dry_run)
            result.files_created.extend(rules_created)
            
            # 3. Generate/update CLAUDE.md bootstrap
            claude_md = self._generate_claude_md(target_path, dry_run)
            if claude_md:
                result.files_created.append(claude_md)
            
            # 4. Update lock state
            if not dry_run:
                self._update_lock_state(scope)
            
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
        
        return result
    
    def _install_skills(self, skills_dir: Path, dry_run: bool) -> list[str]:
        """Install canonical skills to .claude/skills/."""
        created = []
        skills_root = Path(__file__).resolve().parent.parent.parent.parent / "skills"
        
        if not skills_root.exists():
            return created
        
        skills_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy each skill directory
        for category_dir in skills_root.iterdir():
            if not category_dir.is_dir():
                continue
            for skill_dir in category_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                skill_file = skill_dir / "SKILL.md"
                if not skill_file.exists():
                    continue
                
                target_skill_dir = skills_dir / skill_dir.name
                if dry_run:
                    created.append(str(target_skill_dir.relative_to(self.project_root)))
                    continue
                
                # Copy entire skill directory
                if target_skill_dir.exists():
                    shutil.rmtree(target_skill_dir)
                shutil.copytree(skill_dir, target_skill_dir)
                
                created.append(str(target_skill_dir.relative_to(self.project_root)))
                
                # Record in lock state
                self._record_file(self.target, "project", target_skill_dir / "SKILL.md")
        
        return created
    
    def _install_rules(self, target_path: Path, dry_run: bool) -> list[str]:
        """Install path-scoped rules for Python engineering."""
        created = []
        rules_dir = target_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate core Python rules
        rules = [
            ("python-typing.md", self._generate_typing_rule()),
            ("python-testing.md", self._generate_testing_rule()),
            ("python-security.md", self._generate_security_rule()),
            ("python-async.md", self._generate_async_rule()),
            ("python-engineering.md", self._generate_engineering_rule()),
        ]
        
        for filename, content in rules:
            rule_path = rules_dir / filename
            if dry_run:
                created.append(str(rule_path.relative_to(self.project_root)))
                continue
            
            # Add ownership markers
            marked_content = self._wrap_managed(content, rule_path)
            self._safe_write_file(rule_path, marked_content, dry_run)
            created.append(str(rule_path.relative_to(self.project_root)))
            
            if not dry_run:
                self._record_file(self.target, "project", rule_path)
        
        return created
    
    def _generate_claude_md(self, target_path: Path, dry_run: bool) -> Optional[str]:
        """Generate/update CLAUDE.md bootstrap."""
        claude_md = target_path / "CLAUDE.md"
        
        if dry_run:
            return str(claude_md.relative_to(self.project_root))
        
        # Read existing or create new
        existing = ""
        if claude_md.exists():
            existing = claude_md.read_text(encoding="utf-8")
        
        # Generate bootstrap content
        bootstrap = self._generate_claude_md_content()
        
        if existing:
            # Replace or append managed section
            new_content, replaced = self._replace_managed_region(existing, bootstrap, claude_md)
            if replaced:
                self._safe_write_file(claude_md, new_content, dry_run)
                self._record_file(self.target, "project", claude_md, (BEGIN_MARKER, END_MARKER))
                return str(claude_md.relative_to(self.project_root))
            # If no managed region, append
            new_content = existing + "\n\n" + self._wrap_managed(bootstrap, claude_md)
            self._safe_write_file(claude_md, new_content, dry_run)
            self._record_file(self.target, "project", claude_md, (BEGIN_MARKER, END_MARKER))
        else:
            # Create new with bootstrap
            full_content = f"# Project Instructions\n\n{bootstrap}"
            self._safe_write_file(claude_md, self._wrap_managed(full_content, claude_md), dry_run)
            self._record_file(self.target, "project", claude_md, (BEGIN_MARKER, END_MARKER))
        
        return str(claude_md.relative_to(self.project_root))
    
    def _generate_claude_md_content(self) -> str:
        """Generate CLAUDE.md bootstrap content."""
        return """<!-- BEGIN PYTHON-SKILLS MANAGED -->
# Python Skills Integration

This project uses [python-skills](https://github.com/FoxPink-dev/python-skills) for Python engineering standards.

## Available Skills

The following skill categories are available in `.claude/skills/`:

- **core/** - Core Python language patterns
- **stdlib/** - Standard library usage
- **generation/** - Code generation workflows
- **engineering/** - Project engineering practices
- **quality/** - Code quality standards
- **security/** - Security engineering
- **testing/** - Testing methodologies
- **refactoring/** - Safe refactoring patterns
- **debugging/** - Debugging techniques
- **anti_patterns/** - Anti-pattern prevention

## Usage

Skills are loaded automatically when relevant. You can also invoke them directly:

```
/skill-name
```

See `.claude/skills/<skill-name>/SKILL.md` for each skill's description and usage.
<!-- END PYTHON-SKILLS MANAGED -->"""
    
    def _generate_typing_rule(self) -> str:
        return """<!-- BEGIN PYTHON-SKILLS MANAGED -->
---
description: "Python typing engineering guidance"
globs: ["**/*.py"]
alwaysApply: false
---

# Python Typing Standards

## Type Hints
- Use built-in generics (Python 3.9+): `list[str]`, `dict[str, int]`
- Union types: `int | str` (3.10+) or `Union[int, str]`
- Optional: `str | None` not `Optional[str]`

## Protocols & Generics
- Use `Protocol` for structural typing
- `TypeVar` with constraints for generics
- `@dataclass` with type hints

## Validation
- Use Pydantic for runtime validation
- `TypedDict` for structured dicts
<!-- END PYTHON-SKILLS MANAGED -->"""
    
    def _generate_testing_rule(self) -> str:
        return """<!-- BEGIN PYTHON-SKILLS MANAGED -->
---
description: "Python testing best practices"
globs: ["**/*test*.py", "**/test_*.py", "**/*_test.py"]
alwaysApply: false
---

# Testing Standards

## pytest
- Use `pytest` with `pytest-asyncio` for async
- Fixtures in `conftest.py`
- `pytest.mark.parametrize` for parameterized tests

## Coverage
- Target 90%+ branch coverage
- Exclude: `__repr__`, `raise AssertionError`, `if __name__ == "__main__"`

## Async Testing
- Use `pytest-asyncio` mode="auto"
- Test async functions with `await`
<!-- END PYTHON-SKILLS MANAGED -->"""
    
    def _generate_security_rule(self) -> str:
        return """<!-- BEGIN PYTHON-SKILLS MANAGED -->
---
description: "Python security engineering"
globs: ["**/*.py"]
alwaysApply: false
---

# Security Standards

## Input Validation
- Validate all external input at boundaries
- Use allowlists, not blocklists
- Pydantic for API validation

## Injection Prevention
- SQL: parameterized queries only
- Command: list form, no shell=True
- Path: resolve + is_relative_to()
- Deserialization: json/yaml.safe_load only
<!-- END PYTHON-SKILLS MANAGED -->"""
    
    def _generate_async_rule(self) -> str:
        return """<!-- BEGIN PYTHON-SKILLS MANAGED -->
---
description: "Python async/concurrency patterns"
globs: ["**/*.py"]
alwaysApply: false
---

# Async Patterns

## asyncio
- Use `asyncio.gather()` for concurrency
- `asyncio.Semaphore` for limiting
- `asyncio.TaskGroup` (3.11+) for structured concurrency

## Timeouts
- Always set timeouts: `asyncio.wait_for(coro, timeout=5.0)`
- Handle `asyncio.TimeoutError`

## Cancellation
- Check `task.cancelled()` in long operations
- Use `asyncio.shield()` for critical sections
<!-- END PYTHON-SKILLS MANAGED -->"""
    
    def _generate_engineering_rule(self) -> str:
        return """<!-- BEGIN PYTHON-SKILLS MANAGED -->
---
description: "Python engineering practices"
globs: ["**/*.py"]
alwaysApply: false
---

# Engineering Practices

## Project Structure
- Use src-layout: `src/package/`
- `pyproject.toml` with hatchling
- `CLAUDE.md` for project instructions

## Configuration
- Layered: defaults → file → env → CLI
- Pydantic Settings for validation
- Environment variables for secrets

## HTTP Clients
- Use `httpx` (sync + async)
- Connection pooling with limits
- Retry with tenacity/httpx retries

## Packaging
- Use `build` (PEP 517)
- Version from `__version__` in package
- Publish with twine
<!-- END PYTHON-SKILLS MANAGED -->"""
    
    def sync(self, scope: str = "project", dry_run: bool = False) -> SyncResult:
        result = SyncResult(success=True, target=self.target, scope=scope)
        target_path = self._get_scope_path(scope)
        
        try:
            # Reload canonical skills
            skills_root = Path(__file__).resolve().parent.parent.parent.parent / "skills"
            
            # Update skills
            skills_dir = target_path / ".claude" / "skills"
            if skills_dir.exists():
                for skill_dir in skills_dir.iterdir():
                    if skill_dir.is_dir():
                        # Check if skill still exists in canonical
                        canonical = skills_root / skill_dir.name
                        if canonical.exists():
                            # Update if changed
                            pass
                        else:
                            # Skill removed
                            if not dry_run:
                                shutil.rmtree(skill_dir)
                            result.removed.append(str(skill_dir.relative_to(self.project_root)))
                
                # Add new skills
                for category_dir in skills_root.iterdir():
                    if not category_dir.is_dir():
                        continue
                    for skill_dir in category_dir.iterdir():
                        if not skill_dir.is_dir():
                            continue
                        target_skill_dir = skills_dir / skill_dir.name
                        if not target_skill_dir.exists():
                            if not dry_run:
                                shutil.copytree(skill_dir, target_skill_dir)
                            result.added.append(str(target_skill_dir.relative_to(self.project_root)))
            
            # Update lock state
            if not dry_run:
                self._update_lock_state(scope)
                
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
        
        return result
    
    def uninstall(self, scope: str = "project", dry_run: bool = False) -> UninstallResult:
        result = UninstallResult(success=True, target=self.target, scope=scope)
        target_path = self._get_scope_path(scope)
        
        try:
            # Remove .claude/skills/
            skills_dir = target_path / ".claude" / "skills"
            if skills_dir.exists():
                if not dry_run:
                    shutil.rmtree(skills_dir)
                result.files_removed.append(str(skills_dir.relative_to(self.project_root)))
            
            # Remove rules
            rules_dir = target_path / ".claude" / "rules"
            if rules_dir.exists():
                for rule_file in rules_dir.glob("python-*.md"):
                    if self._has_ownership_marker(rule_file):
                        if not dry_run:
                            rule_file.unlink()
                        result.files_removed.append(str(rule_file.relative_to(self.project_root)))
            
            # Remove CLAUDE.md managed section
            claude_md = target_path / "CLAUDE.md"
            if claude_md.exists():
                content = claude_md.read_text(encoding="utf-8")
                new_content, removed = self._remove_managed_region(content, claude_md)
                if removed and not dry_run:
                    self._safe_write_file(claude_md, new_content, dry_run)
                result.regions_removed.append(str(claude_md.relative_to(self.project_root)))
            
            if not dry_run:
                self._update_lock_state(scope)
                
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
        
        return result
    
    def _has_ownership_marker(self, path: Path) -> bool:
        """Check if file has python-skills ownership marker."""
        if not path.exists():
            return False
        content = path.read_text(encoding="utf-8")
        begin, end = self._get_markers(path)
        return begin in content and end in content
    
    def status(self, scope: str = "project") -> StatusResult:
        target_path = self._get_scope_path(scope)
        installed = False
        files = []
        version = ""
        
        # Check skills dir
        skills_dir = target_path / ".claude" / "skills"
        if skills_dir.exists():
            installed = True
            for f in skills_dir.rglob("SKILL.md"):
                files.append(str(f.relative_to(self.project_root)))
        
        # Check rules
        rules_dir = target_path / ".claude" / "rules"
        if rules_dir.exists():
            for f in rules_dir.glob("python-*.md"):
                if self._has_ownership_marker(f):
                    installed = True
                    files.append(str(f.relative_to(self.project_root)))
        
        # Check CLAUDE.md
        claude_md = target_path / "CLAUDE.md"
        if claude_md.exists() and self._has_ownership_marker(claude_md):
            installed = True
            files.append(str(claude_md.relative_to(self.project_root)))
        
        return StatusResult(
            target=self.target,
            scope=scope,
            installed=installed,
            files=files,
            version=self.config.version if hasattr(self.config, 'version') else "1.0.0"
        )
    
    def _update_lock_state(self, scope: str) -> None:
        """Update lock state after changes."""
        self.lock_manager.update_canonical_hash(
            Path(__file__).resolve().parent.parent.parent.parent / "skills"
        )
    
    def _get_markers(self, file_path: Path) -> tuple[str, str]:
        from ..markers import get_markers
        return get_markers(str(file_path))
    
    def _has_ownership_marker(self, path: Path) -> bool:
        if not path.exists():
            return False
        content = path.read_text(encoding="utf-8")
        begin, end = self._get_markers(path)
        return begin in content and end in content