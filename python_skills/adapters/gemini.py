"""Gemini CLI adapter for python-skills."""

from pathlib import Path

from .agent_skills import AgentSkillsAdapter


class GeminiAdapter(AgentSkillsAdapter):
    """Adapter for Google Gemini CLI.
    
    Gemini CLI discovers skills from:
    - .gemini/skills/<name>/SKILL.md (native)
    - .agents/skills/<name>/SKILL.md (cross-agent standard)
    
    We install to .agents/skills/ (shared) and .gemini/skills/ (native).
    """

    target_name = "gemini"
    display_name = "Gemini CLI"
    agent_skills_dir = ".agents/skills"
    native_skills_dir = ".gemini/skills"
    detection_app_command = "gemini"
    detection_project_markers = [".gemini", "GEMINI.md"]

    def _get_global_path(self) -> Path:
        return Path.home() / ".gemini" / "skills"
