"""Universal AGENTS.md adapter for python-skills."""

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


class UniversalAdapter(AgentAdapter):
    """Adapter for Universal AGENTS.md integration."""

    name = "Universal AGENTS.md"
    target = Target.UNIVERSAL.value

    def __init__(self, project_root: Path, skills_registry: SkillRegistry, lock_manager: LockManager, config):
        super().__init__(project_root, skills_registry, lock_manager, config)

    def _get_global_path(self) -> Path:
        return Path.home() / ".agents"

    def detect(self) -> DetectionResult:
        # AGENTS.md is universally supported - no app detection needed
        project_config = (self.project_root / "AGENTS.md").exists()
        global_config = self._get_global_path().exists()

        return DetectionResult(
            application_detected=True,  # Always available
            project_config_detected=project_config,
            adapter_available=True,
            details=f"Universal adapter always available. Project AGENTS.md: {'yes' if project_config else 'no'}"
        )

    def install(self, scope: str = "project", dry_run: bool = False) -> InstallResult:
        result = InstallResult(success=True, target=self.target, scope=scope)
        target_path = self._get_scope_path(scope)

        try:
            agents_md = target_path / "AGENTS.md"
            content = self._generate_agents_md_content()

            if dry_run:
                result.files_created.append(str(agents_md.relative_to(self.project_root)))
            else:
                if agents_md.exists():
                    existing = agents_md.read_text(encoding="utf-8")
                    new_content, replaced = self._replace_managed_region(existing, content, agents_md)
                    if replaced:
                        self._safe_write_file(agents_md, new_content, dry_run)
                    else:
                        new_content = existing + "\n\n" + self._wrap_managed(content, agents_md)
                        self._safe_write_file(agents_md, new_content, dry_run)
                else:
                    self._safe_write_file(agents_md, self._wrap_managed(content, agents_md), dry_run)

                result.files_created.append(str(agents_md.relative_to(self.project_root)))
                self._record_file(self.target, scope, agents_md, (BEGIN_MARKER, END_MARKER))

                if not dry_run:
                    self._update_lock_state(scope)

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def _generate_agents_md_content(self) -> str:
        categories = {}
        for skill in self.skills_registry.get_all_skills():
            if skill.category not in categories:
                categories[skill.category] = []
            categories[skill.category].append(skill.name)

        parts = [
            "<!-- BEGIN PYTHON-SKILLS MANAGED -->",
            "",
            "# Python Skills Integration",
            "",
            "This project uses [python-skills](https://github.com/FoxPink-dev/python-skills) for Python engineering standards.",
            "",
            "## Available Skills",
            "",
            "The canonical skill library is at `python-skills/skills/` with 69 skills across 10 categories.",
            "",
        ]

        for category, skills in sorted(categories.items()):
            cat_parts = [f"### {category.title()}", ""]
            for skill in sorted(skills):
                cat_parts.append(f"- `{skill}`")
            cat_parts.append("")
            parts.extend(cat_parts)

        parts.extend([
            "## Usage",
            "",
            "Reference relevant skills when working on Python code. Skills are loaded on-demand based on task context.",
            "",
            "## Reference",
            "",
            "- Repository: https://github.com/FoxPink-dev/python-skills",
            "- Canonical skills location: `python-skills/skills/` (in python-skills package)",
            "",
            "<!-- END PYTHON-SKILLS MANAGED -->",
        ])

        return "\n".join(parts)

    def sync(self, scope: str = "project", dry_run: bool = False) -> SyncResult:
        result = SyncResult(success=True, target=self.target, scope=scope)
        target_path = self._get_scope_path(scope)
        agents_md = target_path / "AGENTS.md"

        try:
            if not agents_md.exists():
                result.success = False
                result.errors.append("AGENTS.md not found")
                return result

            current = agents_md.read_text(encoding="utf-8")
            new_content = self._generate_agents_md_content()

            # Extract current managed region
            current_managed = self._extract_managed_region(current, agents_md)
            new_managed = self._extract_managed_region(new_content, agents_md)

            if current_managed and new_managed and current_managed.strip() != new_managed.strip():
                new_content, replaced = self._replace_managed_region(current, new_content, agents_md)
                if replaced and not dry_run:
                    self._safe_write_file(agents_md, new_content, dry_run)
                result.modified.append(str(agents_md.relative_to(self.project_root)))
            else:
                result.skipped.append(str(agents_md.relative_to(self.project_root)))

            if not dry_run:
                self._update_lock_state(scope)

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def uninstall(self, scope: str = "project", dry_run: bool = False) -> UninstallResult:
        result = UninstallResult(success=True, target=self.target, scope=scope)
        target_path = self._get_scope_path(scope)
        agents_md = target_path / "AGENTS.md"

        try:
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
