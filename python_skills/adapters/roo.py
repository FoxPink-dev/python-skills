"""Roo Code adapter for python-skills."""

from pathlib import Path

from .agent_skills import AgentSkillsAdapter


class RooAdapter(AgentSkillsAdapter):
    """Adapter for Roo Code (formerly Roo Cline).
    
    Roo Code discovers skills from:
    - .roo/skills/<name>/SKILL.md (native)
    - .agents/skills/<name>/SKILL.md (cross-agent standard)
    
    We install to .agents/skills/ (shared) and .roo/skills/ (native).
    """

    target_name = "roo"
    display_name = "Roo Code"
    agent_skills_dir = ".agents/skills"
    native_skills_dir = ".roo/skills"
    detection_project_markers = [".roo", ".roorules"]

    def _get_global_path(self) -> Path:
        return Path.home() / ".roo" / "skills"
