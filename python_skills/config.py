"""Configuration management for python-skills."""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum


class Scope(str, Enum):
    """Installation scope."""
    PROJECT = "project"
    GLOBAL = "global"


class Target(str, Enum):
    """Target AI coding agent."""
    CLAUDE = "claude"
    CURSOR = "cursor"
    KIRO = "kiro"
    CLINE = "cline"
    UNIVERSAL = "universal"


@dataclass
class AdapterCapabilities:
    """Capabilities of an adapter."""
    supports_project: bool = True
    supports_global: bool = False
    has_native_skills: bool = False
    has_native_rules: bool = False
    supports_path_conditions: bool = False
    safe_uninstall: bool = True


ADAPTER_CAPABILITIES = {
    Target.CLAUDE: AdapterCapabilities(
        supports_project=True,
        supports_global=True,
        has_native_skills=True,
        has_native_rules=True,
        supports_path_conditions=True,
        safe_uninstall=True,
    ),
    Target.CURSOR: AdapterCapabilities(
        supports_project=True,
        supports_global=False,  # User Rules are UI only
        has_native_skills=False,
        has_native_rules=True,
        supports_path_conditions=True,
        safe_uninstall=True,
    ),
    Target.KIRO: AdapterCapabilities(
        supports_project=True,
        supports_global=True,
        has_native_skills=True,
        has_native_rules=True,
        supports_path_conditions=True,
        safe_uninstall=True,
    ),
    Target.CLINE: AdapterCapabilities(
        supports_project=True,
        supports_global=True,
        has_native_skills=False,
        has_native_rules=True,
        supports_path_conditions=True,
        safe_uninstall=True,
    ),
    Target.UNIVERSAL: AdapterCapabilities(
        supports_project=True,
        supports_global=True,
        has_native_skills=False,
        has_native_rules=False,
        supports_path_conditions=False,
        safe_uninstall=True,
    ),
}


@dataclass
class InstallConfig:
    """Configuration for installation."""
    targets: list[Target]
    scope: Scope = Scope.PROJECT
    dry_run: bool = False


@dataclass
class SkillInfo:
    """Information about a skill."""
    name: str
    category: str
    path: Path
    description: str = ""
    triggers: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    priority: str = "primary"
    estimated_tokens: int = 1500


def get_skills_root() -> Path:
    """Get the root directory for canonical skills."""
    # First check if we're in the source tree
    current = Path(__file__).resolve().parent.parent
    skills_dir = current / "skills"
    if skills_dir.exists():
        return skills_dir
    
    # Fallback: try to find via importlib
    import importlib.resources
    try:
        return Path(importlib.resources.files("python_skills") / "skills")
    except Exception:
        pass
    
    # Last resort: current working directory
    return Path.cwd() / "skills"


def get_adapter_capabilities(target: Target) -> AdapterCapabilities:
    """Get capabilities for a target adapter."""
    return ADAPTER_CAPABILITIES.get(target, AdapterCapabilities())