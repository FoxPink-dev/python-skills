"""Cline adapter for python-skills."""

import shutil
from pathlib import Path
from typing import Optional
from ..adapters.base import AgentAdapter, DetectionResult, InstallResult, SyncResult, UninstallResult, StatusResult
from ..config import Target, Scope
from ..skills.registry import SkillRegistry
from ..state import LockManager


class ClineAdapter(AgentAdapter):
    """Adapter for Cline."""
    
    name = "Cline"
    target = Target.CLINE.value
    
    def __init__(self, project_root: Path, skills_registry: SkillRegistry, lock_manager: LockManager, config):
        super().__init__(project_root, skills_registry, lock_manager, config)
    
    def _get_global_path(self) -> Path:
        # Cline global rules location varies by OS
        import platform
        system = platform.system()
        if system == "Windows":
            return Path.home() / "Documents" / "Cline" / "Rules"
        else:
            return Path.home() / "Documents" / "Cline" / "Rules"
    
    def detect(self) -> DetectionResult:
        # Cline is a VS Code extension - check for extension
        app_detected = False
        try:
            # Check if Cline extension is installed
            import subprocess
            result = subprocess.run(["code", "--list-extensions"], capture_output=True, text=True)
            if "cline.cline" in result.stdout.lower():
                app_detected = True
        except Exception:
            pass
        
        project_config = (self.project_root / ".clinerules").exists() or (self.project_root / ".cline" / "rules").exists()
        global_config = self._get_global_path().exists()
        
        return DetectionResult(
            application_detected=app_detected,
            project_config_detected=project_config,
            adapter_available=True,
            details=f"App: {'yes' if app_detected else 'no'}, Project: {'yes' if project_config else 'no'}, Global: {'yes' if global_config else 'no'}"
        )
    
    def install(self, scope: str = "project", dry_run: bool = False) -> InstallResult:
        result = InstallResult(success=True, target=self.target, scope=scope)
        target_path = self._get_scope_path(scope)
        
        try:
            # Generate .clinerules/python-skills.md with path conditionals
            rules_dir = target_path / ".clinerules"
            rules_dir.mkdir(parents=True, exist_ok=True)
            
            rule_path = rules_dir / "python-skills.md"
            content = self._generate_cline_rule()
            
            if dry_run:
                result.files_created.append(str(rule_path.relative_to(self.project_root)))
            else:
                self._safe_write_file(rule_path, content, dry_run)
                result.files_created.append(str(rule_path.relative_to(self.project_root)))
                self._record_file(self.target, scope, rule_path)
            
            # Generate AGENTS.md bootstrap
            agents_md = self._generate_agents_md(target_path, dry_run)
            if agents_md:
                result.files_created.append(agents_md)
            
            if not dry_run:
                self._update_lock_state(scope)
                
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
        
        return result
    
    def _generate_cline_rule(self) -> str:
        categories = {}
        for skill in self.skills_registry.get_all_skills():
            if skill.category not in categories:
                categories[skill.category] = []
            categories[skill.category].append(skill.name)
        
        parts = [
            "---",
            "paths:",
            '  - "**/*.py"',
            "---",
            "",
            "<!-- BEGIN PYTHON-SKILLS MANAGED -->",
            "",
            "# Python Skills Integration",
            "",
            "This project uses [python-skills](https://github.com/FoxPink-dev/python-skills) for Python engineering standards.",
            "",
            "## Available Skill Categories",
            "",
        ]
        
        for category, skills in sorted(categories.items()):
            parts.append(f"### {category.title()}")
            parts.append("")
            for skill in sorted(skills):
                parts.append(f"- `{skill}`")
            parts.append("")
        
        parts.extend([
            "## Usage",
            "",
            "Reference relevant skills when working on Python code. Key patterns:",
            "",
            "- **Type hints**: Use built-in generics, `str | None`, `Protocol`",
            "- **Async**: `asyncio.gather`, `Semaphore`, `TaskGroup` (3.11+)",
            "- **HTTP**: `httpx` with retries, timeouts, connection pooling",
            "- **Security**: Parameterized queries, `pathlib` for paths, `yaml.safe_load`",
            "- **Testing**: `pytest` with parametrized tests, edge cases",
            "- **CLI**: `click`/`typer`, config layering, secrets via env",
            "",
            "Reference: [python-skills repository](https://github.com/FoxPink-dev/python-skills)",
            "",
            "<!-- END PYTHON-SKILLS MANAGED -->",
        ])
        
        return "\n".join(parts)
    
    def _generate_agents_md(self, target_path: Path, dry_run: bool) -> Optional[str]:
        agents_md = target_path / "AGENTS.md"
        bootstrap = self._generate_agents_md_content()
        
        if dry_run:
            return str(agents_md.relative_to(self.project_root))
        
        if agents_md.exists():
            existing = agents_md.read_text(encoding="utf-8")
            new_content, replaced = self._replace_managed_region(existing, bootstrap, agents_md)
            if replaced:
                self._safe_write_file(agents_md, new_content, dry_run)
                self._record_file(self.target, "project", agents_md, (BEGIN_MARKER, END_MARKER))
            else:
                new_content = existing + "\n\n" + self._wrap_managed(bootstrap, agents_md)
                self._safe_write_file(agents_md, new_content, dry_run)
                self._record_file(self.target, "project", agents_md, (BEGIN_MARKER, END_MARKER))
        else:
            self._safe_write_file(agents_md, self._wrap_managed(bootstrap, agents_md), dry_run)
            self._record_file(self.target, "project", agents_md, (BEGIN_MARKER, END_MARKER))
        
        return str(agents_md.relative_to(self.project_root))
    
    def _generate_agents_md_content(self) -> str:
        return """<!-- BEGIN PYTHON-SKILLS MANAGED -->
# Python Skills Integration

This project uses [python-skills](https://github.com/FoxPink-dev/python-skills) for Python engineering standards.

## Available Skills

The canonical skill library is at `python-skills/skills/` with 69 skills across 10 categories.

### Core
- variables_types, control_flow, functions, data_structures, oop, comprehensions, advanced_python

### Stdlib
- argparse, collections, datetime, functools, itertools, json, logging, os_sys, pathlib, re, statistics, subprocess

### Generation
- type_hints, protocols_generics, async_concurrency, error_handling, validation_pipeline, workflow

### Engineering
- cli_apps, configuration, database, dependency_management, http_clients, logging, modules_packages, packaging, project_structure, pyproject_toml, virtual_environments

### Quality
- abstractions, comments, documentation, duplication, functions, maintainability, naming, readability, type_annotations

### Security
- auth_boundaries, command_injection, dependency_risks, file_handling, input_validation, path_traversal, secrets, sql_injection, unsafe_deserialization

### Testing
- async_tests, coverage, edge_cases, fixtures_mocks, organization, parameterized, regression_tests

### Refactoring
- behavior_preservation, incremental, interface_stability, safe_refactoring

### Debugging
- common_bugs, inspection_techniques, root_cause

### Anti-Patterns
- index

## Usage
Reference relevant skills when working on Python code. Skills are loaded on-demand based on task context.
<!-- END PYTHON-SKILLS MANAGED -->"""
    
    def sync(self, scope: str = "project", dry_run: bool = False) -> SyncResult:
        result = SyncResult(success=True, target=self.target, scope=scope)
        target_path = self._get_scope_path(scope)
        
        try:
            rules_dir = target_path / ".clinerules"
            rule_path = rules_dir / "python-skills.md"
            
            if rule_path.exists():
                current = rule_path.read_text(encoding="utf-8")
                new_content = self._generate_cline_rule()
                
                if current.strip() != new_content.strip():
                    if not dry_run:
                        self._safe_write_file(rule_path, new_content, dry_run)
                    result.modified.append(str(rule_path.relative_to(self.project_root)))
                else:
                    result.skipped.append(str(rule_path.relative_to(self.project_root)))
            
            # Sync AGENTS.md
            agents_md = target_path / "AGENTS.md"
            if agents_md.exists():
                current = agents_md.read_text(encoding="utf-8")
                new_agents = self._generate_agents_md_content()
                new_content, replaced = self._replace_managed_region(current, new_agents, agents_md)
                if replaced and not dry_run:
                    self._safe_write_file(agents_md, new_content, dry_run)
                    result.modified.append(str(agents_md.relative_to(self.project_root)))
            
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
            rules_dir = target_path / ".clinerules"
            rule_path = rules_dir / "python-skills.md"
            
            if rule_path.exists() and self._has_ownership_marker(rule_path):
                if not dry_run:
                    rule_path.unlink()
                result.files_removed.append(str(rule_path.relative_to(self.project_root)))
            
            # Remove AGENTS.md section
            agents_md = target_path / "AGENTS.md"
            if agents_md.exists():
                content = agents_md.read_text(encoding="utf-8")
                new_content, removed = self._remove_managed_region(content, agents_md)
                if removed and not dry_run:
                    self._safe_write_file(agents_md, new_content, dry_run)
                result.regions_removed.append(str(agents_md.relative_to(self.project_root)))
            
            if not dry_run:
                self._update_lock_state(scope)
                
        except Exception as e:
            result.success = False
            result.errors.append(str(e))
        
        return result
    
    def status(self, scope: str = "project") -> StatusResult:
        target_path = self._get_scope_path(scope)
        installed = False
        files = []
        
        rule_path = target_path / ".clinerules" / "python-skills.md"
        if rule_path.exists() and self._has_ownership_marker(rule_path):
            installed = True
            files.append(str(rule_path.relative_to(self.project_root)))
        
        agents_md = target_path / "AGENTS.md"
        if agents_md.exists() and self._has_ownership_marker(agents_md):
            installed = True
            files.append(str(agents_md.relative_to(self.project_root)))
        
        return StatusResult(
            target=self.target,
            scope=scope,
            installed=installed,
            files=files,
            version="1.0.0"
        )
    
    def _update_lock_state(self, scope: str) -> None:
        self.lock_manager.update_canonical_hash(
            Path(__file__).resolve().parent.parent.parent.parent / "skills"
        )