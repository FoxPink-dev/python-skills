"""VS Code / GitHub Copilot adapter for python-skills."""

from pathlib import Path

from .agent_skills import AgentSkillsAdapter


class VSCodeAdapter(AgentSkillsAdapter):
    """Adapter for VS Code / GitHub Copilot.
    
    VS Code / Copilot discovers skills from:
    - .agents/skills/<name>/SKILL.md (cross-agent standard)
    - .github/skills/<name>/SKILL.md (native)
    - .claude/skills/<name>/SKILL.md (Claude Code compat)
    
    We install to .agents/skills/ (shared) and .github/skills/ (native).
    """

    target_name = "vscode"
    display_name = "VS Code / GitHub Copilot"
    agent_skills_dir = ".agents/skills"
    native_skills_dir = ".github/skills"
    detection_app_command = "code"
    detection_project_markers = [".github", ".vscode"]

    def _get_global_path(self) -> Path:
        return Path.home() / ".copilot" / "skills"
