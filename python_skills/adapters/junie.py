"""JetBrains / Junie adapter for python-skills."""

from pathlib import Path

from .agent_skills import AgentSkillsAdapter


class JunieAdapter(AgentSkillsAdapter):
    """Adapter for JetBrains AI / Junie.
    
    Junie discovers skills from:
    - .junie/skills/<name>/SKILL.md (native)
    - .agents/skills/<name>/SKILL.md (cross-agent standard)
    
    We install to .agents/skills/ (shared) and .junie/skills/ (native).
    """

    target_name = "jetbrains"
    display_name = "JetBrains / Junie"
    agent_skills_dir = ".agents/skills"
    native_skills_dir = ".junie/skills"
    detection_project_markers = [".junie"]

    def _get_global_path(self) -> Path:
        return Path.home() / ".junie" / "skills"
