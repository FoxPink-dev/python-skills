"""Kiro adapter for python-skills."""

import shutil
from pathlib import Path

from ..adapters.base import (
    AgentAdapter,
    DetectionResult,
    InstallResult,
    StatusResult,
    SyncResult,
    UninstallResult,
)
from ..config import Target
from ..markers import BEGIN_MARKER, END_MARKER
from ..skills.registry import SkillRegistry
from ..state import LockManager


class KiroAdapter(AgentAdapter):
    """Adapter for Kiro."""

    name = "Kiro"
    target = Target.KIRO.value

    def __init__(self, project_root: Path, skills_registry: SkillRegistry, lock_manager: LockManager, config):
        super().__init__(project_root, skills_registry, lock_manager, config)

    def _get_global_path(self) -> Path:
        return Path.home() / ".kiro"

    def detect(self) -> DetectionResult:
        app_detected = shutil.which("kiro") is not None
        project_config = (self.project_root / ".kiro").exists()
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
            # 1. Install native skills to .kiro/skills/
            skills_dir = target_path / ".kiro" / "skills"
            skills_created = self._install_skills(skills_dir, dry_run)
            result.files_created.extend(skills_created)

            # 2. Generate steering file for routing
            steering_dir = target_path / ".kiro" / "steering"
            steering_created = self._install_steering(steering_dir, dry_run)
            result.files_created.extend(steering_created)

            # 3. Generate AGENTS.md bootstrap
            agents_md = self._generate_agents_md(target_path, dry_run)
            if agents_md:
                result.files_created.append(agents_md)

            if not dry_run:
                self._update_lock_state(scope)

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def _install_skills(self, skills_dir: Path, dry_run: bool) -> list[str]:
        created = []
        skills_root = self.skills_registry.skills_root

        if not skills_root.exists():
            return created

        skills_dir.mkdir(parents=True, exist_ok=True)

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

                if target_skill_dir.exists():
                    shutil.rmtree(target_skill_dir)
                shutil.copytree(skill_dir, target_skill_dir)

                created.append(str(target_skill_dir.relative_to(self.project_root)))

                if not dry_run:
                    self._record_file(self.target, "project", target_skill_dir / "SKILL.md")

        return created

    def _install_steering(self, steering_dir: Path, dry_run: bool) -> list[str]:
        created = []
        steering_dir.mkdir(parents=True, exist_ok=True)

        # Generate main steering file
        steering_path = steering_dir / "python-skills.md"
        content = self._generate_steering_content()

        if dry_run:
            created.append(str(steering_path.relative_to(self.project_root)))
        else:
            self._safe_write_file(steering_path, content, dry_run)
            created.append(str(steering_path.relative_to(self.project_root)))
            self._record_file(self.target, "project", steering_path)

        return created

    def _generate_steering_content(self) -> str:
        categories = {}
        for skill in self.skills_registry.get_all_skills():
            if skill.category not in categories:
                categories[skill.category] = []
            categories[skill.category].append(skill.name)

        parts = [
            "---",
            "inclusion: auto",
            "name: python-skills",
            "description: Python engineering skills and patterns",
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
            parts = [f"### {category.title()}", ""]
            for skill in sorted(skills):
                parts.append(f"- `{skill}`")
            parts.append("")
            parts.extend(parts)

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

    def _generate_agents_md(self, target_path: Path, dry_run: bool) -> str | None:
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
            skills_root = self.skills_registry.skills_root

            # Sync skills
            skills_dir = target_path / ".kiro" / "skills"
            if skills_dir.exists():
                for skill_dir in skills_dir.iterdir():
                    if skill_dir.is_dir():
                        canonical = skills_root / skill_dir.name
                        if canonical.exists():
                            # Check if changed (could use hash comparison)
                            pass
                        else:
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

            # Sync steering
            steering_dir = target_path / ".kiro" / "steering"
            steering_file = steering_dir / "python-skills.md"
            if steering_file.exists():
                current = steering_file.read_text(encoding="utf-8")
                new_content = self._generate_steering_content()
                if current.strip() != new_content.strip():
                    if not dry_run:
                        self._safe_write_file(steering_file, new_content, dry_run)
                    result.modified.append(str(steering_file.relative_to(self.project_root)))

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
            # Remove skills
            skills_dir = target_path / ".kiro" / "skills"
            if skills_dir.exists():
                if not dry_run:
                    shutil.rmtree(skills_dir)
                result.files_removed.append(str(skills_dir.relative_to(self.project_root)))

            # Remove steering
            steering_dir = target_path / ".kiro" / "steering"
            steering_file = steering_dir / "python-skills.md"
            if steering_file.exists() and self._has_ownership_marker(steering_file):
                if not dry_run:
                    steering_file.unlink()
                result.files_removed.append(str(steering_file.relative_to(self.project_root)))

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

        skills_dir = target_path / ".kiro" / "skills"
        if skills_dir.exists():
            installed = True
            for f in skills_dir.rglob("SKILL.md"):
                files.append(str(f.relative_to(self.project_root)))

        steering_file = target_path / ".kiro" / "steering" / "python-skills.md"
        if steering_file.exists() and self._has_ownership_marker(steering_file):
            installed = True
            files.append(str(steering_file.relative_to(self.project_root)))

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

    def _has_ownership_marker(self, path: Path) -> bool:
        """Check if a file has our ownership markers."""
        if not path.exists():
            return False
        content = path.read_text(encoding="utf-8")
        begin, end = self._get_markers(path)
        return begin in content and end in content

    def _update_lock_state(self, scope: str) -> None:
        self.lock_manager.update_canonical_hash(self.skills_registry.skills_root)
