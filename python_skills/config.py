"""Configuration management for python-skills."""

from dataclasses import dataclass
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
    OPENCODE = "opencode"
    WINDSURF = "windsurf"
    VSCODE = "vscode"
    ROO = "roo"
    GEMINI = "gemini"
    CODEX = "codex"
    JETBRAINS = "jetbrains"
    GOOSE = "goose"
    ZED = "zed"
    CONTINUE = "continue"
    AIDER = "aider"
    UNIVERSAL = "universal"


@dataclass
class AdapterCapabilities:
    """Capabilities of an adapter."""
    supports_project: bool = True
    supports_global: bool = False
    has_native_skills: bool = False
    has_native_rules: bool = False
    has_native_instructions: bool = False
    supports_path_conditions: bool = False
    supports_file_references: bool = False
    supports_manual_activation: bool = False
    supports_auto_activation: bool = True
    supports_cli: bool = False
    supports_ide: bool = False
    safe_uninstall: bool = True
    adapter_class: str = "E"  # A=NativeSkills, B=NativeRules, C=NativeInstructions, D=Config, E=Universal


ADAPTER_CAPABILITIES = {
    Target.CLAUDE: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_skills=True, has_native_rules=True,
        has_native_instructions=True, supports_path_conditions=True,
        supports_file_references=True, supports_cli=True,
        adapter_class="A",
    ),
    Target.CURSOR: AdapterCapabilities(
        supports_project=True, supports_global=False,
        has_native_rules=True, supports_path_conditions=True,
        supports_ide=True, adapter_class="B",
    ),
    Target.KIRO: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_skills=True, has_native_rules=True,
        has_native_instructions=True, supports_path_conditions=True,
        supports_ide=True, adapter_class="A",
    ),
    Target.CLINE: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_skills=True, has_native_rules=True,
        has_native_instructions=True, supports_path_conditions=True,
        supports_ide=True, adapter_class="A",
    ),
    Target.OPENCODE: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_skills=True, has_native_instructions=True,
        supports_file_references=True,
        supports_cli=True, supports_ide=True,
        adapter_class="A",
    ),
    Target.WINDSURF: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_skills=True, has_native_rules=True,
        has_native_instructions=True, supports_path_conditions=True,
        supports_ide=True, adapter_class="A",
    ),
    Target.VSCODE: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_skills=True, has_native_rules=True,
        has_native_instructions=True, supports_path_conditions=True,
        supports_file_references=True,
        supports_cli=True, supports_ide=True,
        adapter_class="A",
    ),
    Target.ROO: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_skills=True, has_native_rules=True,
        has_native_instructions=True,
        supports_ide=True, adapter_class="A",
    ),
    Target.GEMINI: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_skills=True, has_native_instructions=True,
        supports_file_references=True,
        supports_cli=True, adapter_class="A",
    ),
    Target.CODEX: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_skills=True, has_native_instructions=True,
        supports_cli=True, adapter_class="A",
    ),
    Target.JETBRAINS: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_skills=True, has_native_instructions=True,
        supports_ide=True, adapter_class="A",
    ),
    Target.GOOSE: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_skills=True, has_native_instructions=True,
        supports_file_references=True,
        supports_cli=True, adapter_class="A",
    ),
    Target.ZED: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_skills=True, has_native_instructions=True,
        supports_ide=True, adapter_class="A",
    ),
    Target.CONTINUE: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_rules=True, has_native_instructions=True,
        supports_path_conditions=True,
        supports_ide=True, adapter_class="B",
    ),
    Target.AIDER: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_instructions=True,
        supports_cli=True, adapter_class="D",
    ),
    Target.UNIVERSAL: AdapterCapabilities(
        supports_project=True, supports_global=True,
        has_native_instructions=True,
        supports_cli=True, supports_ide=True,
        adapter_class="E",
    ),
}


@dataclass
class InstallConfig:
    """Configuration for installation."""
    targets: list[Target]
    scope: Scope = Scope.PROJECT
    dry_run: bool = False


def get_adapter_capabilities(target: Target) -> AdapterCapabilities:
    """Get capabilities for a target adapter."""
    return ADAPTER_CAPABILITIES.get(target, AdapterCapabilities())
