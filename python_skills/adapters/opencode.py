"""OpenCode adapter for python-skills."""

from pathlib import Path

from .agent_skills import AgentSkillsAdapter


class OpenCodeAdapter(AgentSkillsAdapter):
    """Adapter for OpenCode (CLI/TUI/Desktop).
    
    OpenCode discovers skills from:
    - .agents/skills/<name>/SKILL.md (cross-agent standard)
    - .opencode/skills/<name>/SKILL.md (native, fallback)
    - .claude/skills/<name>/SKILL.md (Claude Code compat)
    
    We install to .agents/skills/ (shared). OpenCode discovers from the
    shared directory natively, so no separate native directory is needed.
    """

    target_name = "opencode"
    display_name = "OpenCode"
    agent_skills_dir = ".agents/skills"
    native_skills_dir = None
    detection_app_command = "opencode"
    detection_project_markers = [".opencode", "opencode.json", "opencode.jsonc"]

    def _get_global_path(self) -> Path:
        return Path.home() / ".config" / "opencode" / "skills"
