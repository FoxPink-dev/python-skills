"""Goose adapter for python-skills."""

from pathlib import Path

from .agent_skills import AgentSkillsAdapter


class GooseAdapter(AgentSkillsAdapter):
    """Adapter for Goose (by Block/Square).
    
    Goose discovers skills from:
    - .agents/skills/<name>/SKILL.md (cross-agent standard)
    - .goose/skills/<name>/SKILL.md (backward compat)
    - .claude/skills/<name>/SKILL.md (backward compat)
    
    We install to .agents/skills/ (shared).
    """

    target_name = "goose"
    display_name = "Goose"
    agent_skills_dir = ".agents/skills"
    detection_app_command = "goose"
    detection_project_markers = [".goosehints", "AGENTS.md"]

    def _get_global_path(self) -> Path:
        return Path.home() / ".config" / "goose" / "skills"
