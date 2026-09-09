"""Continue adapter for python-skills.

Continue uses a native rules system (.continue/rules/) and reads
AGENTS.md/AGENT.md/CLAUDE.md as fallback instructions.
It does NOT have a native skills system.
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


class ContinueAdapter(AgentAdapter):
    """Adapter for Continue.
    
    Continue uses rules (.continue/rules/*.md) not skills.
    We generate a consolidated Python rules file.
    """

    name = "Continue"
    target = Target.CONTINUE.value

    def __init__(self, project_root: Path, skills_registry: SkillRegistry,
                 lock_manager: LockManager, config):
        super().__init__(project_root, skills_registry, lock_manager, config)

    def _get_global_path(self) -> Path:
        return Path.home() / ".continue" / "rules"

    def detect(self) -> DetectionResult:
        import shutil
        app_detected = shutil.which("continue") is not None
        project_config = (self.project_root / ".continue").exists()
        global_config = self._get_global_path().exists()

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
            rules_dir = target_path / ".continue" / "rules"
            rules_dir.mkdir(parents=True, exist_ok=True)

            rule_path = rules_dir / "python-skills.md"
            content = self._generate_rule()

            if dry_run:
                result.files_created.append(str(rule_path.relative_to(self.project_root)))
            else:
                self._safe_write_file(rule_path, content, dry_run)
                result.files_created.append(str(rule_path.relative_to(self.project_root)))
                self._record_file(self.target, scope, rule_path)

            if not dry_run:
                self._update_lock_state(scope)

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def _generate_rule(self) -> str:
        categories = {}
        if self.skills_registry:
            for skill in self.skills_registry.get_all_skills():
                if skill.category not in categories:
                    categories[skill.category] = []
                categories[skill.category].append(skill.name)

        parts = [
            "---",
            "alwaysApply: true",
            "---",
            "",
            "<!-- BEGIN PYTHON-SKILLS MANAGED -->",
            "",
            "# Python Skills Integration",
            "",
            "This project uses python-skills for Python engineering standards.",
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

    def sync(self, scope: str = "project", dry_run: bool = False) -> SyncResult:
        result = SyncResult(success=True, target=self.target, scope=scope)
        target_path = self._get_scope_path(scope)

        try:
            rule_path = target_path / ".continue" / "rules" / "python-skills.md"
            if not rule_path.exists():
                result.success = False
                result.errors.append("python-skills.md not found")
                return result

            current = rule_path.read_text(encoding="utf-8")
            new_content = self._generate_rule()

            if current.strip() != new_content.strip():
                if not dry_run:
                    self._safe_write_file(rule_path, new_content, dry_run)
                result.modified.append(str(rule_path.relative_to(self.project_root)))
            else:
                result.skipped.append(str(rule_path.relative_to(self.project_root)))

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
            rule_path = target_path / ".continue" / "rules" / "python-skills.md"
            if rule_path.exists():
                content = rule_path.read_text(encoding="utf-8")
                begin, end = self._get_markers(rule_path)
                if begin in content:
                    if not dry_run:
                        rule_path.unlink()
                    result.files_removed.append(str(rule_path.relative_to(self.project_root)))

            if not dry_run:
                self._update_lock_state(scope)

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def status(self, scope: str = "project") -> StatusResult:
        target_path = self._get_scope_path(scope)
        rule_path = target_path / ".continue" / "rules" / "python-skills.md"

        installed = False
        files = []
        if rule_path.exists():
            content = rule_path.read_text(encoding="utf-8")
            begin, end = self._get_markers(rule_path)
            if begin in content:
                installed = True
                files.append(str(rule_path.relative_to(self.project_root)))

        return StatusResult(
            target=self.target, scope=scope, installed=installed,
            files=files, version="2.0.0",
        )

    def _update_lock_state(self, scope: str) -> None:
        skills_root = Path(__file__).resolve().parent.parent.parent.parent / "skills"
        if skills_root.exists():
            self.lock_manager.update_canonical_hash(skills_root)
