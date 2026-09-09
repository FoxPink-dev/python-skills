"""Codex CLI adapter for python-skills."""

from pathlib import Path

from .agent_skills import AgentSkillsAdapter


class CodexAdapter(AgentSkillsAdapter):
    """Adapter for OpenAI Codex CLI.
    
    Codex CLI discovers skills from:
    - .agents/skills/<name>/SKILL.md (cross-agent standard)
    
    Codex is the primary architect of AGENTS.md.
    """

    target_name = "codex"
    display_name = "Codex CLI"
    agent_skills_dir = ".agents/skills"
    detection_app_command = "codex"
    detection_project_markers = ["AGENTS.md"]

    def _get_global_path(self) -> Path:
        return Path.home() / ".agents" / "skills"
