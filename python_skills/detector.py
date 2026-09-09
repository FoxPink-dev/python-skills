"""Environment detection for AI coding agents."""

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from python_skills.adapters.base import DetectionResult
from python_skills.config import Target


@dataclass
class DetectionSummary:
    """Summary of detection results for all targets."""
    targets: dict[str, DetectionResult] = field(default_factory=dict)

    def get_available_targets(self) -> list[str]:
        """Get list of targets with detected application."""
        return [name for name, result in self.targets.items() if result.application_detected]


class EnvironmentDetector:
    """Detects AI coding agent environments and configurations."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()

    def detect_all(self) -> DetectionSummary:
        """Detect all supported AI coding agents."""
        summary = DetectionSummary()

        # Existing targets
        summary.targets[Target.CLAUDE.value] = self._detect_claude()
        summary.targets[Target.CURSOR.value] = self._detect_cursor()
        summary.targets[Target.KIRO.value] = self._detect_kiro()
        summary.targets[Target.CLINE.value] = self._detect_cline()

        # Phase 4 targets
        summary.targets[Target.OPENCODE.value] = self._detect_app("opencode", [".opencode", "opencode.json", "opencode.jsonc"])
        summary.targets[Target.WINDSURF.value] = self._detect_dir_only([".windsurf", ".devin"])
        summary.targets[Target.VSCODE.value] = self._detect_app("code", [".github", ".vscode"])
        summary.targets[Target.ROO.value] = self._detect_dir_only([".roo", ".roorules"])
        summary.targets[Target.GEMINI.value] = self._detect_app("gemini", [".gemini", "GEMINI.md"])
        summary.targets[Target.CODEX.value] = self._detect_app("codex", ["AGENTS.md"])
        summary.targets[Target.JETBRAINS.value] = self._detect_dir_only([".junie"])
        summary.targets[Target.GOOSE.value] = self._detect_app("goose", [".goosehints", "AGENTS.md"])
        summary.targets[Target.ZED.value] = self._detect_app("zed", ["AGENTS.md", ".agents"])
        summary.targets[Target.CONTINUE.value] = self._detect_dir_only([".continue"])
        summary.targets[Target.AIDER.value] = self._detect_app("aider", [".aider.conf.yml"])

        # Universal (always available)
        summary.targets[Target.UNIVERSAL.value] = DetectionResult(
            application_detected=True,
            project_config_detected=(self.project_root / "AGENTS.md").exists(),
            adapter_available=True,
            details="Universal adapter always available",
        )

        return summary

    def _detect_app(self, command: str, project_markers: list[str]) -> DetectionResult:
        """Detect application by command and project markers."""
        app_detected = shutil.which(command) is not None
        project_config = any((self.project_root / m).exists() for m in project_markers)

        return DetectionResult(
            application_detected=app_detected,
            project_config_detected=project_config,
            adapter_available=True,
            details=f"App: {'yes' if app_detected else 'no'}, Project: {'yes' if project_config else 'no'}",
        )

    def _detect_dir_only(self, project_markers: list[str]) -> DetectionResult:
        """Detect by project markers only (no CLI command)."""
        project_config = any((self.project_root / m).exists() for m in project_markers)

        return DetectionResult(
            application_detected=False,
            project_config_detected=project_config,
            adapter_available=True,
            details=f"App: IDE extension, Project: {'yes' if project_config else 'no'}",
        )

    def _detect_claude(self) -> DetectionResult:
        """Detect Claude Code."""
        app_detected = shutil.which("claude") is not None
        project_config = (self.project_root / ".claude").exists()
        global_config = (Path.home() / ".claude").exists()

        return DetectionResult(
            application_detected=app_detected,
            project_config_detected=project_config,
            adapter_available=True,
            details=f"App: {'yes' if app_detected else 'no'}, Project: {'yes' if project_config else 'no'}, Global: {'yes' if global_config else 'no'}"
        )

    def _detect_cursor(self) -> DetectionResult:
        """Detect Cursor."""
        app_detected = shutil.which("cursor") is not None
        project_config = (self.project_root / ".cursor").exists() or (self.project_root / ".cursorrules").exists()

        return DetectionResult(
            application_detected=app_detected,
            project_config_detected=project_config,
            adapter_available=True,
            details=f"App: {'yes' if app_detected else 'no'}, Project: {'yes' if project_config else 'no'}"
        )

    def _detect_kiro(self) -> DetectionResult:
        """Detect Kiro."""
        app_detected = shutil.which("kiro") is not None
        project_config = (self.project_root / ".kiro").exists()
        global_config = (Path.home() / ".kiro").exists()

        return DetectionResult(
            application_detected=app_detected,
            project_config_detected=project_config,
            adapter_available=True,
            details=f"App: {'yes' if app_detected else 'no'}, Project: {'yes' if project_config else 'no'}, Global: {'yes' if global_config else 'no'}"
        )

    def _detect_cline(self) -> DetectionResult:
        """Detect Cline."""
        app_detected = False
        try:
            result = subprocess.run(
                ["code", "--list-extensions"],
                capture_output=True, text=True, timeout=5
            )
            if "cline.cline" in result.stdout.lower():
                app_detected = True
        except Exception:
            pass

        project_config = (
            (self.project_root / ".clinerules").exists() or
            (self.project_root / ".cline").exists() or
            (self.project_root / ".agents" / "skills").exists()
        )

        return DetectionResult(
            application_detected=app_detected,
            project_config_detected=project_config,
            adapter_available=True,
            details=f"App: {'yes' if app_detected else 'no'}, Project: {'yes' if project_config else 'no'}"
        )


def detect_environment(project_root: Path) -> 'DetectionSummary':
    """Convenience function to detect all environments."""
    detector = EnvironmentDetector(project_root)
    return detector.detect_all()
