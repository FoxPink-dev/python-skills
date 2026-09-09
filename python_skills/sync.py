"""Sync logic for python-skills."""

from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
from ..adapters.base import SyncResult
from ..skills.registry import SkillRegistry
from ..state import LockManager
from ..config import Target, Scope


class SyncManager:
    """Manages synchronization of installed skills with canonical source."""
    
    def __init__(self, project_root: Path, skills_registry: SkillRegistry, lock_manager: LockManager):
        self.project_root = Path(project_root).resolve()
        self.skills_registry = skills_registry
        self.lock_manager = lock_manager
        self.skills_root = self._find_skills_root()
    
    def _find_skills_root(self) -> Path:
        """Find the canonical skills root."""
        current = Path(__file__).resolve().parent.parent.parent
        skills_root = current / "skills"
        if skills_root.exists():
            return skills_root
        return Path.cwd() / "skills"
    
    def sync_all(self, scope: Scope = Scope.PROJECT, 
                 targets: Optional[List[Target]] = None,
                 dry_run: bool = False) -> dict[Target, SyncResult]:
        """Sync all or specified targets."""
        results = {}
        
        if targets is None:
            # Sync all installed targets
            targets = [Target(t) for t in self.lock_manager.get_all_targets().keys() 
                       if t in [t.value for t in Target]]
        
        for target in targets:
            from ..adapters import get_adapter
            adapter = get_adapter(target, self.project_root, self.skills_registry, self.lock_manager, None)
            result = adapter.sync(scope=scope.value, dry_run=dry_run)
            results[target] = result
        
        return results
    
    def sync_target(self, target: Target, scope: Scope = Scope.PROJECT, 
                    dry_run: bool = False) -> SyncResult:
        """Sync a single target."""
        from ..adapters import get_adapter
        adapter = get_adapter(target, self.project_root, None, self.lock_manager, None)
        return adapter.sync(scope=scope.value, dry_run=dry_run)


def get_adapter(target: Target, project_root: Path, skills_registry, lock_manager, config):
    """Factory function to get adapter instance."""
    from ..adapters.claude import ClaudeAdapter
    from ..adapters.cursor import CursorAdapter
    from ..adapters.kiro import KiroAdapter
    from ..adapters.cline import ClineAdapter
    from ..adapters.universal import UniversalAdapter
    
    adapters = {
        Target.CLAUDE: lambda: ClaudeAdapter(project_root, skills_registry, lock_manager, config),
        Target.CURSOR: lambda: CursorAdapter(project_root, skills_registry, lock_manager, config),
        Target.KIRO: lambda: KiroAdapter(project_root, skills_registry, lock_manager, config),
        Target.CLINE: lambda: ClineAdapter(project_root, skills_registry, lock_manager, config),
        Target.UNIVERSAL: lambda: UniversalAdapter(project_root, skills_registry, lock_manager, config),
    }
    
    if target not in adapters:
        raise ValueError(f"Unknown target: {target}")
    
    return adapters[target]()