"""Base adapter contract for python-skills adapters."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DetectionResult:
    """Result of environment detection."""
    application_detected: bool
    project_config_detected: bool
    adapter_available: bool = True
    details: str = ""


@dataclass
class InstallResult:
    """Result of installation."""
    success: bool
    target: str
    scope: str
    files_created: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class SyncResult:
    """Result of synchronization."""
    success: bool
    target: str
    scope: str
    added: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class UninstallResult:
    """Result of uninstallation."""
    success: bool
    target: str
    scope: str
    files_removed: list[str] = field(default_factory=list)
    regions_removed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class StatusResult:
    """Result of status check."""
    target: str
    scope: str
    installed: bool
    files: list[str] = field(default_factory=list)
    version: str = ""
    last_sync: str = ""


class AgentAdapter(ABC):
    """Abstract base class for agent adapters."""

    name: str = ""
    target: str = ""

    def __init__(self, project_root: Path, skills_registry, lock_manager, config):
        self.project_root = Path(project_root).resolve()
        self.skills_registry = skills_registry
        self.lock_manager = lock_manager
        self.config = config

    @abstractmethod
    def detect(self) -> DetectionResult:
        """Detect if this agent is available and configured."""
        pass

    @abstractmethod
    def install(self, scope: str = "project", dry_run: bool = False) -> InstallResult:
        """Install integration for this agent."""
        pass

    @abstractmethod
    def sync(self, scope: str = "project", dry_run: bool = False) -> SyncResult:
        """Synchronize installed integration with current skills."""
        pass

    @abstractmethod
    def uninstall(self, scope: str = "project", dry_run: bool = False) -> UninstallResult:
        """Uninstall integration for this agent."""
        pass

    @abstractmethod
    def status(self, scope: str = "project") -> StatusResult:
        """Get installation status."""
        pass

    def _get_scope_path(self, scope: str) -> Path:
        """Get the path for a given scope."""
        if scope == "global":
            return self._get_global_path()
        return self.project_root

    @abstractmethod
    def _get_global_path(self) -> Path:
        """Get the global config path for this agent."""
        pass

    def _get_markers(self, file_path: Path) -> tuple[str, str]:
        """Get ownership markers for a file."""
        from ..markers import get_markers
        return get_markers(str(file_path))

    def _wrap_managed(self, content: str, file_path: Path) -> str:
        """Wrap content with ownership markers."""
        from ..markers import wrap_managed_content
        return wrap_managed_content(content, str(file_path))

    def _replace_managed_region(self, content: str, new_content: str, file_path: Path) -> tuple[str, bool]:
        """Replace managed region in content."""
        from ..markers import replace_managed_region
        return replace_managed_region(content, new_content, str(file_path))

    def _remove_managed_region(self, content: str, file_path: Path) -> tuple[str, bool]:
        """Remove managed region from content."""
        from ..markers import remove_managed_region
        return remove_managed_region(content, str(file_path))

    def _extract_managed_region(self, content: str, file_path: Path) -> str | None:
        """Extract managed region from content."""
        from ..markers import extract_managed_region
        return extract_managed_region(content, str(file_path))

    def _safe_write_file(self, path: Path, content: str, dry_run: bool = False) -> bool:
        """Safely write a file with ownership markers."""
        if dry_run:
            return True

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return True

    def _record_file(self, target: str, scope: str, path: Path, region_markers: tuple = None) -> None:
        """Record a managed file in the lock state."""
        self.lock_manager.record_file(target, scope, path, region_markers)


