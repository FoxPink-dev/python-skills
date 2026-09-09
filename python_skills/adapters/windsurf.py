"""Windsurf adapter for python-skills."""

from pathlib import Path

from .agent_skills import AgentSkillsAdapter


class WindsurfAdapter(AgentSkillsAdapter):
    """Adapter for Windsurf (Devin Desktop/Cascade).
    
    Windsurf discovers skills from:
    - .agents/skills/<name>/SKILL.md (cross-agent standard)
    - .windsurf/skills/<name>/SKILL.md (native, fallback)
    - .claude/skills/<name>/SKILL.md (Claude Code compat)
    
    We install to .agents/skills/ (shared). Windsurf discovers from the
    shared directory natively, so no separate native directory is needed.
    """

    target_name = "windsurf"
    display_name = "Windsurf"
    agent_skills_dir = ".agents/skills"
    native_skills_dir = None
    detection_project_markers = [".windsurf", ".devin"]

    def _get_global_path(self) -> Path:
        return Path.home() / ".codeium" / "windsurf" / "skills"
