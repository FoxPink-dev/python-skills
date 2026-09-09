"""Cline adapter for python-skills.

Cline supports both:
1. .clinerules/ (rules-based, legacy)
2. .cline/skills/<name>/SKILL.md (Agent Skills, native)
3. .agents/skills/<name>/SKILL.md (cross-agent standard)

This adapter installs both rules AND skills for maximum compatibility.
"""

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
from ..skills.registry import SkillRegistry
from ..state import LockManager


class ClineAdapter(AgentAdapter):
    """Adapter for Cline.
    
    Installs:
    - .agents/skills/<name>/SKILL.md (Agent Skills)
    - .cline/skills/<name>/SKILL.md (native)
    - .clinerules/python-skills.md (rules, backward compat)
    """

    name = "Cline"
    target = Target.CLINE.value

    def __init__(self, project_root: Path, skills_registry: SkillRegistry, lock_manager: LockManager, config):
        super().__init__(project_root, skills_registry, lock_manager, config)

    def _get_global_path(self) -> Path:
        import platform
        system = platform.system()
        if system == "Windows":
            return Path.home() / "Documents" / "Cline" / "Rules"
        else:
            return Path.home() / "Documents" / "Cline" / "Rules"

    def detect(self) -> DetectionResult:
        app_detected = False
        try:
            import subprocess
            result = subprocess.run(["code", "--list-extensions"], capture_output=True, text=True)
            if "cline.cline" in result.stdout.lower():
                app_detected = True
        except Exception:
            pass

        project_config = (
            (self.project_root / ".clinerules").exists() or
            (self.project_root / ".cline").exists() or
            (self.project_root / ".agents" / "skills").exists()
        )
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
            # 1. Install Agent Skills to .agents/skills/
            agents_skills_dir = target_path / ".agents" / "skills"
            agents_created = self._install_skills_to_dir(agents_skills_dir, dry_run)
            result.files_created.extend(agents_created)

            # 2. Install Agent Skills to .cline/skills/ (native)
            cline_skills_dir = target_path / ".cline" / "skills"
            cline_created = self._install_skills_to_dir(cline_skills_dir, dry_run)
            result.files_created.extend(cline_created)

            # 3. Generate rules file (backward compat)
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

            if not dry_run:
                self._update_lock_state(scope)

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def _install_skills_to_dir(self, skills_dir: Path, dry_run: bool) -> list[str]:
        """Install canonical skills as Agent Skills SKILL.md files."""
        from .agent_skills import _generate_skill_md, _skill_name_to_slug
        created = []

        if not self.skills_registry:
            return created

        skills_dir.mkdir(parents=True, exist_ok=True)

        for skill in self.skills_registry.get_all_skills():
            slug = _skill_name_to_slug(skill.name)
            target_skill_dir = skills_dir / slug
            target_skill_file = target_skill_dir / "SKILL.md"

            if dry_run:
                created.append(str(target_skill_file.relative_to(self.project_root)))
                continue

            content = self.skills_registry.get_skill_content(skill.name)
            if not content:
                continue

            skill_md = _generate_skill_md(skill, content)

            target_skill_dir.mkdir(parents=True, exist_ok=True)
            target_skill_file.write_text(skill_md, encoding="utf-8")

            created.append(str(target_skill_file.relative_to(self.project_root)))
            self._record_file(self.target, "project", target_skill_file)

        return created

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
            "This project uses python-skills for Python engineering standards.",
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
            "Reference relevant skills when working on Python code.",
            "",
            "<!-- END PYTHON-SKILLS MANAGED -->",
        ])

        return "\n".join(parts)

    def sync(self, scope: str = "project", dry_run: bool = False) -> SyncResult:
        result = SyncResult(success=True, target=self.target, scope=scope)
        target_path = self._get_scope_path(scope)

        try:
            # Sync skills in .agents/skills/
            agents_skills_dir = target_path / ".agents" / "skills"
            if agents_skills_dir.exists():
                for item in agents_skills_dir.iterdir():
                    if item.is_dir() and (item / "SKILL.md").exists():
                        if not dry_run:
                            shutil.rmtree(item)
                        result.removed.append(str(item.relative_to(self.project_root)))

            # Re-install skills
            agents_created = self._install_skills_to_dir(agents_skills_dir, dry_run)
            result.added.extend(agents_created)

            cline_skills_dir = target_path / ".cline" / "skills"
            if cline_skills_dir.exists():
                for item in cline_skills_dir.iterdir():
                    if item.is_dir() and (item / "SKILL.md").exists():
                        if not dry_run:
                            shutil.rmtree(item)
                        result.removed.append(str(item.relative_to(self.project_root)))

            cline_created = self._install_skills_to_dir(cline_skills_dir, dry_run)
            result.added.extend(cline_created)

            # Sync rules
            rule_path = target_path / ".clinerules" / "python-skills.md"
            if rule_path.exists():
                current = rule_path.read_text(encoding="utf-8")
                new_content = self._generate_cline_rule()
                if current.strip() != new_content.strip():
                    if not dry_run:
                        self._safe_write_file(rule_path, new_content, dry_run)
                    result.modified.append(str(rule_path.relative_to(self.project_root)))

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
            # Remove .agents/skills/ managed content
            agents_skills_dir = target_path / ".agents" / "skills"
            if agents_skills_dir.exists():
                for item in agents_skills_dir.iterdir():
                    if item.is_dir():
                        skill_file = item / "SKILL.md"
                        if skill_file.exists():
                            content = skill_file.read_text(encoding="utf-8")
                            begin, end = self._get_markers(skill_file)
                            if begin in content:
                                if not dry_run:
                                    shutil.rmtree(item)
                                result.files_removed.append(str(item.relative_to(self.project_root)))

            # Remove .cline/skills/ managed content
            cline_skills_dir = target_path / ".cline" / "skills"
            if cline_skills_dir.exists():
                for item in cline_skills_dir.iterdir():
                    if item.is_dir():
                        skill_file = item / "SKILL.md"
                        if skill_file.exists():
                            content = skill_file.read_text(encoding="utf-8")
                            begin, end = self._get_markers(skill_file)
                            if begin in content:
                                if not dry_run:
                                    shutil.rmtree(item)
                                result.files_removed.append(str(item.relative_to(self.project_root)))

            # Remove rules
            rule_path = target_path / ".clinerules" / "python-skills.md"
            if rule_path.exists() and self._has_ownership_marker(rule_path):
                if not dry_run:
                    rule_path.unlink()
                result.files_removed.append(str(rule_path.relative_to(self.project_root)))

            if not dry_run:
                self._update_lock_state(scope)

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def _has_ownership_marker(self, path: Path) -> bool:
        if not path.exists():
            return False
        content = path.read_text(encoding="utf-8")
        begin, end = self._get_markers(path)
        return begin in content and end in content

    def status(self, scope: str = "project") -> StatusResult:
        target_path = self._get_scope_path(scope)
        installed = False
        files = []

        # Check .agents/skills/
        agents_skills_dir = target_path / ".agents" / "skills"
        if agents_skills_dir.exists():
            for item in agents_skills_dir.iterdir():
                if item.is_dir():
                    skill_file = item / "SKILL.md"
                    if skill_file.exists():
                        content = skill_file.read_text(encoding="utf-8")
                        begin, end = self._get_markers(skill_file)
                        if begin in content:
                            installed = True
                            files.append(str(skill_file.relative_to(self.project_root)))

        # Check .cline/skills/
        cline_skills_dir = target_path / ".cline" / "skills"
        if cline_skills_dir.exists():
            for item in cline_skills_dir.iterdir():
                if item.is_dir():
                    skill_file = item / "SKILL.md"
                    if skill_file.exists():
                        content = skill_file.read_text(encoding="utf-8")
                        begin, end = self._get_markers(skill_file)
                        if begin in content:
                            installed = True
                            files.append(str(skill_file.relative_to(self.project_root)))

        # Check .clinerules/
        rule_path = target_path / ".clinerules" / "python-skills.md"
        if rule_path.exists() and self._has_ownership_marker(rule_path):
            installed = True
            files.append(str(rule_path.relative_to(self.project_root)))

        return StatusResult(
            target=self.target, scope=scope, installed=installed,
            files=files, version="2.0.0"
        )

    def _update_lock_state(self, scope: str) -> None:
        self.lock_manager.update_canonical_hash(
            Path(__file__).resolve().parent.parent.parent.parent / "skills"
        )
