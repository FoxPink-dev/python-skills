"""Aider adapter for python-skills.

Aider uses a "declare-everything" model — no auto-discovery of instruction files.
Integration is via `read:` key in `.aider.conf.yml` or `--read` CLI flag.
"""

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
from ..skills.registry import SkillRegistry
from ..state import LockManager


class AiderAdapter(AgentAdapter):
    """Adapter for Aider.
    
    Aider does not auto-discover instruction files. We generate:
    1. A PYTHON_SKILLS.md summary file
    2. Update .aider.conf.yml to read it
    """

    name = "Aider"
    target = Target.AIDER.value

    def __init__(self, project_root: Path, skills_registry: SkillRegistry,
                 lock_manager: LockManager, config):
        super().__init__(project_root, skills_registry, lock_manager, config)

    def _get_global_path(self) -> Path:
        return Path.home()

    def detect(self) -> DetectionResult:
        import shutil
        app_detected = shutil.which("aider") is not None
        project_config = (self.project_root / ".aider.conf.yml").exists()
        global_config = (Path.home() / ".aider.conf.yml").exists()

        return DetectionResult(
            application_detected=app_detected,
            project_config_detected=project_config,
            adapter_available=True,
            details=f"App: {'yes' if app_detected else 'no'}, "
                    f"Project: {'yes' if project_config else 'no'}, "
                    f"Global: {'yes' if global_config else 'no'}",
        )

    def install(self, scope: str = "project", dry_run: bool = False) -> InstallResult:
        result = InstallResult(success=True, target=self.target, scope=scope)
        target_path = self._get_scope_path(scope)

        try:
            # Generate PYTHON_SKILLS.md
            skills_md = target_path / "PYTHON_SKILLS.md"
            content = self._generate_skills_summary()

            if dry_run:
                result.files_created.append(str(skills_md.relative_to(self.project_root)))
            else:
                self._safe_write_file(skills_md, content, dry_run)
                result.files_created.append(str(skills_md.relative_to(self.project_root)))
                self._record_file(self.target, scope, skills_md)

            # Update .aider.conf.yml
            config_path = target_path / ".aider.conf.yml"
            config_created = self._update_aider_config(config_path, dry_run)
            if config_created:
                result.files_created.append(config_created)

            if not dry_run:
                self._update_lock_state(scope)

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def _generate_skills_summary(self) -> str:
        categories = {}
        if self.skills_registry:
            for skill in self.skills_registry.get_all_skills():
                if skill.category not in categories:
                    categories[skill.category] = []
                categories[skill.category].append(skill.name)

        parts = [
            "<!-- BEGIN PYTHON-SKILLS MANAGED -->",
            "# Python Skills Integration",
            "",
            "This project uses python-skills for Python engineering standards.",
            "",
            "## Available Skills",
            "",
        ]

        for category, skills in sorted(categories.items()):
            parts.append(f"### {category.title()}")
            parts.append("")
            for skill in sorted(skills):
                parts.append(f"- `{skill}`")
            parts.append("")

        parts.extend([
            "## Key Patterns",
            "",
            "- **Type hints**: Use built-in generics, `str | None`, `Protocol`",
            "- **Async**: `asyncio.gather`, `Semaphore`, `TaskGroup` (3.11+)",
            "- **HTTP**: `httpx` with retries, timeouts, connection pooling",
            "- **Security**: Parameterized queries, `pathlib` for paths, `yaml.safe_load`",
            "- **Testing**: `pytest` with parametrized tests, edge cases",
            "",
            "<!-- END PYTHON-SKILLS MANAGED -->",
        ])

        return "\n".join(parts)

    def _update_aider_config(self, config_path: Path, dry_run: bool) -> str | None:
        """Update .aider.conf.yml to read PYTHON_SKILLS.md."""
        import yaml

        existing = {}
        if config_path.exists():
            try:
                existing = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            except Exception:
                existing = {}

        read_list = existing.get("read", [])
        if not isinstance(read_list, list):
            read_list = [read_list] if read_list else []

        if "PYTHON_SKILLS.md" not in read_list:
            read_list.append("PYTHON_SKILLS.md")
            existing["read"] = read_list

            if not dry_run:
                content = yaml.dump(existing, default_flow_style=False, sort_keys=True)
                self._safe_write_file(config_path, content, dry_run)

            return str(config_path.relative_to(self.project_root))

        return None

    def sync(self, scope: str = "project", dry_run: bool = False) -> SyncResult:
        result = SyncResult(success=True, target=self.target, scope=scope)
        target_path = self._get_scope_path(scope)

        try:
            skills_md = target_path / "PYTHON_SKILLS.md"
            if not skills_md.exists():
                result.success = False
                result.errors.append("PYTHON_SKILLS.md not found")
                return result

            current = skills_md.read_text(encoding="utf-8")
            new_content = self._generate_skills_summary()

            if current.strip() != new_content.strip():
                if not dry_run:
                    self._safe_write_file(skills_md, new_content, dry_run)
                result.modified.append(str(skills_md.relative_to(self.project_root)))
            else:
                result.skipped.append(str(skills_md.relative_to(self.project_root)))

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
            skills_md = target_path / "PYTHON_SKILLS.md"
            if skills_md.exists():
                content = skills_md.read_text(encoding="utf-8")
                begin, end = self._get_markers(skills_md)
                if begin in content:
                    if not dry_run:
                        skills_md.unlink()
                    result.files_removed.append(str(skills_md.relative_to(self.project_root)))

            if not dry_run:
                self._update_lock_state(scope)

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def status(self, scope: str = "project") -> StatusResult:
        target_path = self._get_scope_path(scope)
        skills_md = target_path / "PYTHON_SKILLS.md"

        installed = False
        files = []
        if skills_md.exists():
            content = skills_md.read_text(encoding="utf-8")
            begin, end = self._get_markers(skills_md)
            if begin in content:
                installed = True
                files.append(str(skills_md.relative_to(self.project_root)))

        return StatusResult(
            target=self.target, scope=scope, installed=installed,
            files=files, version="2.0.0",
        )

    def _update_lock_state(self, scope: str) -> None:
        skills_root = self.skills_registry.skills_root
        if skills_root.exists():
            self.lock_manager.update_canonical_hash(skills_root)
