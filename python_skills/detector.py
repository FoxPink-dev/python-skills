"""Environment detection for AI coding agents."""

import shutil
import subprocess
import platform
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from python_skills.config import Target
from python_skills.adapters.base import DetectionResult


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
        
        # Detect each target
        summary.targets[Target.CLAUDE.value] = self._detect_claude()
        summary.targets[Target.CURSOR.value] = self._detect_cursor()
        summary.targets[Target.KIRO.value] = self._detect_kiro()
        summary.targets[Target.CLINE.value] = self._detect_cline()
        summary.targets[Target.UNIVERSAL.value] = self._detect_universal()
        
        return summary
    
    def _detect_claude(self) -> DetectionResult:
        """Detect Claude Code."""
        # Check if claude is in PATH
        app_detected = shutil.which("claude") is not None
        
        # Check for project config
        project_config = (self.project_root / ".claude").exists()
        
        # Check for global config
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
            (self.project_root / ".cline" / "rules").exists()
        )
        
        # Determine global path by OS
        system = platform.system()
        if system == "Windows":
            global_path = Path.home() / "Documents" / "Cline" / "Rules"
        else:
            global_path = Path.home() / "Documents" / "Cline" / "Rules"
        global_config = global_path.exists()
        
        return DetectionResult(
            application_detected=app_detected,
            project_config_detected=project_config,
            adapter_available=True,
            details=f"App: {'yes' if app_detected else 'no'}, Project: {'yes' if project_config else 'no'}, Global: {'yes' if global_config else 'no'}"
        )
    
    def _detect_universal(self) -> DetectionResult:
        """Universal AGENTS.md is always available."""
        project_config = (self.project_root / "AGENTS.md").exists()
        global_config = (Path.home() / ".agents" / "AGENTS.md").exists()
        
        return DetectionResult(
            application_detected=True,
            project_config_detected=project_config,
            adapter_available=True,
            details=f"Universal adapter always available. Project AGENTS.md: {'yes' if project_config else 'no'}"
        )


def detect_environment(project_root: Path) -> 'DetectionSummary':
    """Convenience function to detect all environments."""
    detector = EnvironmentDetector(project_root)
    return detector.detect_all()