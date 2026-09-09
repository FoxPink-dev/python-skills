"""Shared Agent Skills adapter for targets supporting the Agent Skills specification.

The Agent Skills specification (https://agentskills.io) defines:
- SKILL.md with YAML frontmatter (name, description required)
- Directory-based skill structure with optional supporting files
- Progressive disclosure (metadata first, full content on demand)

This base class handles:
- Converting canonical flat .md skills to Agent Skills SKILL.md format
- Installing skills to target-specific discovery paths
- Sync, uninstall, and status operations
- Ownership tracking via markers
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
from ..skills.metadata import SkillMetadata
from ..skills.registry import SkillRegistry
from ..state import LockManager


def _skill_name_to_slug(name: str) -> str:
    """Convert a skill name to an Agent Skills compliant slug.
    
    Agent Skills spec: lowercase alphanumeric with single hyphen separators.
    """
    slug = name.lower()
    slug = slug.replace("_", "-")
    # Remove consecutive hyphens
    while "--" in slug:
        slug = slug.replace("--", "-")
    # Strip leading/trailing hyphens
    slug = slug.strip("-")
    # Ensure it's valid
    if not slug:
        slug = "skill"
    return slug


def _generate_skill_md(skill: SkillMetadata, content: str) -> str:
    """Generate Agent Skills compliant SKILL.md from a canonical skill.
    
    Adds YAML frontmatter if missing, preserves existing content.
    """
    # Check if content already has frontmatter
    if content.startswith("---"):
        return content

    # Generate frontmatter
    slug = _skill_name_to_slug(skill.name)
    description = skill.description or f"Python {skill.category} skill: {skill.name}"

    # Truncate description to 1024 chars (Agent Skills spec limit)
    if len(description) > 1024:
        description = description[:1021] + "..."

    frontmatter = f"""---
name: {slug}
description: {description}
---"""

    return f"{frontmatter}\n\n{content}"


class AgentSkillsAdapter(AgentAdapter):
    """Base adapter for targets supporting the Agent Skills specification.
    
    Subclasses define:
    - target_name: Target enum value
    - display_name: Human-readable name
    - agent_skills_dir: Project-level path for SKILL.md files (e.g., ".agents/skills")
    - global_skills_dir: Global path for SKILL.md files
    - detection_project_markers: Files/dirs that indicate project integration
    - detection_app_command: CLI command to check for app detection
    """

    # Subclasses must set these
    target_name: str = ""
    display_name: str = ""
    agent_skills_dir: str = ".agents/skills"
    global_skills_dir: str = ""
    detection_project_markers: list[str] = []
    detection_app_command: str | None = None
    # Additional target-native skill directory (e.g., ".opencode/skills")
    native_skills_dir: str | None = None

    def __init__(self, project_root: Path, skills_registry: SkillRegistry,
                 lock_manager: LockManager, config):
        super().__init__(project_root, skills_registry, lock_manager, config)

    def _get_global_path(self) -> Path:
        if self.global_skills_dir:
            return Path.home() / self.global_skills_dir
        return Path.home() / ".agents"

    def detect(self) -> DetectionResult:
        """Detect if this agent is available and configured."""
        import shutil as _shutil

        app_detected = False
        if self.detection_app_command:
            app_detected = _shutil.which(self.detection_app_command) is not None

        project_config = any(
            (self.project_root / marker).exists()
            for marker in self.detection_project_markers
        )

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
        """Install Agent Skills for this target."""
        result = InstallResult(success=True, target=self.target_name, scope=scope)
        target_path = self._get_scope_path(scope)

        try:
            # 1. Install skills to .agents/skills/
            skills_dir = target_path / self.agent_skills_dir
            created = self._install_skills_to_dir(skills_dir, dry_run)
            result.files_created.extend(created)

            # 2. If target has a native skills dir that differs, also install there
            if self.native_skills_dir and self.native_skills_dir != self.agent_skills_dir:
                native_dir = target_path / self.native_skills_dir
                native_created = self._install_skills_to_dir(native_dir, dry_run)
                result.files_created.extend(native_created)

            # 3. Generate instructions file if the target supports it
            instructions_created = self._install_instructions(target_path, dry_run)
            result.files_created.extend(instructions_created)

            if not dry_run:
                self._update_lock_state(scope)

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def _install_skills_to_dir(self, skills_dir: Path, dry_run: bool) -> list[str]:
        """Install all canonical skills to a target skills directory."""
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

            # Get canonical content
            content = self.skills_registry.get_skill_content(skill.name)
            if not content:
                continue

            # Generate Agent Skills compliant SKILL.md
            skill_md = _generate_skill_md(skill, content)

            # Wrap with ownership markers for status/uninstall detection
            skill_md = self._wrap_managed(skill_md, target_skill_file)

            # Write to target
            target_skill_dir.mkdir(parents=True, exist_ok=True)
            target_skill_file.write_text(skill_md, encoding="utf-8")

            created.append(str(target_skill_file.relative_to(self.project_root)))
            self._record_file(self.target_name, "project", target_skill_file)

        return created

    def _install_instructions(self, target_path: Path, dry_run: bool) -> list[str]:
        """Generate instructions file for the target. Override in subclasses."""
        return []

    def sync(self, scope: str = "project", dry_run: bool = False) -> SyncResult:
        """Sync installed skills with canonical source."""
        result = SyncResult(success=True, target=self.target_name, scope=scope)
        target_path = self._get_scope_path(scope)

        try:
            skills_dir = target_path / self.agent_skills_dir

            if not skills_dir.exists():
                result.success = False
                result.errors.append(f"No {self.agent_skills_dir} directory found")
                return result

            # Get current installed skills
            installed = set()
            for item in skills_dir.iterdir():
                if item.is_dir() and (item / "SKILL.md").exists():
                    installed.add(item.name)

            # Get canonical skills
            canonical = set()
            if self.skills_registry:
                for skill in self.skills_registry.get_all_skills():
                    slug = _skill_name_to_slug(skill.name)
                    canonical.add(slug)

            # Remove skills no longer in canonical
            for skill_name in installed:
                if skill_name not in canonical:
                    skill_dir = skills_dir / skill_name
                    if not dry_run:
                        shutil.rmtree(skill_dir)
                    result.removed.append(str(skill_dir.relative_to(self.project_root)))

            # Add new skills
            for slug in canonical:
                if slug not in installed:
                    skill = self.skills_registry.get_skill(slug.replace("-", "_"))
                    if skill:
                        target_dir = skills_dir / slug
                        if not dry_run:
                            content = self.skills_registry.get_skill_content(skill.name)
                            if content:
                                skill_md = _generate_skill_md(skill, content)
                                skill_md = self._wrap_managed(skill_md, target_dir / "SKILL.md")
                                target_dir.mkdir(parents=True, exist_ok=True)
                                (target_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
                        result.added.append(str((target_dir / "SKILL.md").relative_to(self.project_root)))

            # Update existing skills
            for slug in canonical & installed:
                skill = self.skills_registry.get_skill(slug.replace("-", "_"))
                if skill:
                    skill_file = skills_dir / slug / "SKILL.md"
                    if skill_file.exists():
                        current = skill_file.read_text(encoding="utf-8")
                        content = self.skills_registry.get_skill_content(skill.name)
                        if content:
                            new_content = _generate_skill_md(skill, content)
                            # Wrap with markers for comparison and writing
                            new_content_wrapped = self._wrap_managed(new_content, skill_file)
                            # Strip markers from current to compare raw content
                            begin, end = self._get_markers(skill_file)
                            current_raw = current
                            if begin in current and end in current:
                                start = current.find(begin) + len(begin)
                                end_idx = current.find(end, start)
                                if end_idx != -1:
                                    current_raw = current[start:end_idx].strip()
                            new_raw = new_content
                            if current_raw.strip() != new_raw.strip():
                                if not dry_run:
                                    skill_file.write_text(new_content_wrapped, encoding="utf-8")
                                result.modified.append(str(skill_file.relative_to(self.project_root)))
                            else:
                                result.skipped.append(str(skill_file.relative_to(self.project_root)))

            if not dry_run:
                self._update_lock_state(scope)

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def uninstall(self, scope: str = "project", dry_run: bool = False) -> UninstallResult:
        """Uninstall skills managed by python-skills.
        
        For shared directories (.agents/skills/), only removes the vendor-specific
        native directory. The shared directory is preserved for other consumers.
        """
        result = UninstallResult(success=True, target=self.target_name, scope=scope)
        target_path = self._get_scope_path(scope)

        try:
            # Remove vendor-specific native skills dir (e.g., .opencode/skills/)
            if self.native_skills_dir and self.native_skills_dir != self.agent_skills_dir:
                native_dir = target_path / self.native_skills_dir
                if native_dir.exists():
                    for item in native_dir.iterdir():
                        if item.is_dir():
                            skill_file = item / "SKILL.md"
                            if skill_file.exists():
                                content = skill_file.read_text(encoding="utf-8")
                            begin, _end = self._get_markers(skill_file)
                            if begin in content:
                                if not dry_run:
                                    shutil.rmtree(item)
                                result.files_removed.append(
                                    str(item.relative_to(self.project_root))
                                )

            # For the shared .agents/skills/ dir: only remove if this target
            # is the sole consumer. Check lock file for other consumers.
            skills_dir = target_path / self.agent_skills_dir
            if skills_dir.exists() and self.agent_skills_dir == ".agents/skills":
                # Check if any other target still references .agents/skills/
                other_consumers = self._count_other_consumers(scope)
                if other_consumers > 0:
                    # Other consumers exist — don't touch shared dir
                    pass
                else:
                    # No other consumers — safe to remove shared dir
                    for item in skills_dir.iterdir():
                        if item.is_dir():
                            skill_file = item / "SKILL.md"
                            if skill_file.exists():
                                content = skill_file.read_text(encoding="utf-8")
                                begin, _end = self._get_markers(skill_file)
                                if begin in content:
                                    if not dry_run:
                                        shutil.rmtree(item)
                                    result.files_removed.append(
                                        str(item.relative_to(self.project_root))
                                    )
            elif skills_dir.exists():
                # Non-shared agent_skills_dir — remove normally
                for item in skills_dir.iterdir():
                    if item.is_dir():
                        skill_file = item / "SKILL.md"
                        if skill_file.exists():
                            content = skill_file.read_text(encoding="utf-8")
                            begin, _end = self._get_markers(skill_file)
                            if begin in content:
                                if not dry_run:
                                    shutil.rmtree(item)
                                result.files_removed.append(
                                    str(item.relative_to(self.project_root))
                                )

            if not dry_run:
                self._update_lock_state(scope)

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def _count_other_consumers(self, scope: str) -> int:
        """Count how many other targets use the shared .agents/skills/ directory."""
        # Known targets that consume .agents/skills/
        shared_consumers = {
            "opencode", "windsurf", "vscode", "gemini",
            "roo", "codex", "goose", "jetbrains", "zed",
        }
        # Remove self from the count
        other = shared_consumers - {self.target_name}
        # Check which others are actually installed (have lock records)
        count = 0
        for consumer in other:
            status = self.lock_manager.get_target_status(consumer)
            if status and status.files:
                count += 1
        return count

    def status(self, scope: str = "project") -> StatusResult:
        """Get installation status."""
        target_path = self._get_scope_path(scope)
        installed = False
        files = []

        skills_dir = target_path / self.agent_skills_dir
        if skills_dir.exists():
            for item in skills_dir.iterdir():
                if item.is_dir():
                    skill_file = item / "SKILL.md"
                    if skill_file.exists():
                        content = skill_file.read_text(encoding="utf-8")
                        begin, end = self._get_markers(skill_file)
                        if begin in content:
                            installed = True
                            files.append(str(skill_file.relative_to(self.project_root)))

        return StatusResult(
            target=self.target_name,
            scope=scope,
            installed=installed,
            files=files,
            version="2.0.0",
        )

    def _update_lock_state(self, scope: str) -> None:
        """Update lock state after changes."""
        skills_root = Path(__file__).resolve().parent.parent.parent.parent / "skills"
        if skills_root.exists():
            self.lock_manager.update_canonical_hash(skills_root)
