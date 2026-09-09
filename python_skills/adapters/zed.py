"""Zed adapter for python-skills."""

from pathlib import Path

from .agent_skills import AgentSkillsAdapter


class ZedAdapter(AgentSkillsAdapter):
    """Adapter for Zed editor.
    
    Zed discovers skills from:
    - .agents/skills/<name>/SKILL.md (Agent Skills spec)
    
    Zed also reads AGENTS.md for instructions.
    """

    target_name = "zed"
    display_name = "Zed"
    agent_skills_dir = ".agents/skills"
    detection_app_command = "zed"
    detection_project_markers = ["AGENTS.md", ".agents"]

    def _get_global_path(self) -> Path:
        import platform
        if platform.system() == "Windows":
            return Path.home() / "AppData" / "Roaming" / "Zed" / "skills"
        return Path.home() / ".config" / "zed" / "skills"
