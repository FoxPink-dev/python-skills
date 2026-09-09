"""Adapters for python-skills target environments."""

from ..config import Target


def get_adapter(target: Target, project_root, skills_registry, lock_manager, config):
    """Factory function to get adapter instance by target."""
    from .aider_adapter import AiderAdapter
    from .claude import ClaudeAdapter
    from .cline import ClineAdapter
    from .codex import CodexAdapter
    from .continue_adapter import ContinueAdapter
    from .cursor import CursorAdapter
    from .gemini import GeminiAdapter
    from .goose import GooseAdapter
    from .junie import JunieAdapter
    from .kiro import KiroAdapter
    from .opencode import OpenCodeAdapter
    from .roo import RooAdapter
    from .universal import UniversalAdapter
    from .vscode import VSCodeAdapter
    from .windsurf import WindsurfAdapter
    from .zed import ZedAdapter

    adapters = {
        Target.CLAUDE: ClaudeAdapter,
        Target.CURSOR: CursorAdapter,
        Target.KIRO: KiroAdapter,
        Target.CLINE: ClineAdapter,
        Target.UNIVERSAL: UniversalAdapter,
        Target.OPENCODE: OpenCodeAdapter,
        Target.WINDSURF: WindsurfAdapter,
        Target.VSCODE: VSCodeAdapter,
        Target.ROO: RooAdapter,
        Target.GEMINI: GeminiAdapter,
        Target.CODEX: CodexAdapter,
        Target.JETBRAINS: JunieAdapter,
        Target.GOOSE: GooseAdapter,
        Target.ZED: ZedAdapter,
        Target.CONTINUE: ContinueAdapter,
        Target.AIDER: AiderAdapter,
    }

    adapter_cls = adapters.get(target)
    if adapter_cls is None:
        raise ValueError(f"Unknown target: {target}")

    return adapter_cls(project_root, skills_registry, lock_manager, config)
