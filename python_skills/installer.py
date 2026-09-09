"""Installer orchestration for python-skills."""

from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, field

from python_skills.config import Target, Scope, InstallConfig, get_adapter_capabilities
from python_skills.adapters.base import InstallResult, DetectionResult
from python_skills.detector import EnvironmentDetector, DetectionSummary
from python_skills.adapters.claude import ClaudeAdapter
from python_skills.adapters.cursor import CursorAdapter
from python_skills.adapters.kiro import KiroAdapter
from python_skills.adapters.cline import ClineAdapter
from python_skills.adapters.universal import UniversalAdapter
from python_skills.skills.registry import SkillRegistry, get_registry
from python_skills.state import LockManager
from python_skills.config import get_adapter_capabilities


@dataclass
class InstallPlan:
    """Plan for installation."""
    targets: dict[Target, Scope]
    dry_run: bool = False


class SkillInstaller:
    """Orchestrates installation of python-skills across multiple agents."""
    
    def __init__(self, project_root: Path, config: InstallConfig):
        self.project_root = Path(project_root).resolve()
        self.config = config
        self.detector = EnvironmentDetector(self.project_root)
        self.skills_registry = get_registry()
        self.lock_manager = LockManager(self.project_root)
        
        # Initialize adapters
        self.adapters = {
            Target.CLAUDE: ClaudeAdapter(self.project_root, self.skills_registry, self.lock_manager, config),
            Target.CURSOR: CursorAdapter(self.project_root, self.skills_registry, self.lock_manager, config),
            Target.KIRO: KiroAdapter(self.project_root, self.skills_registry, self.lock_manager, config),
            Target.CLINE: ClineAdapter(self.project_root, self.skills_registry, self.lock_manager, config),
            Target.UNIVERSAL: UniversalAdapter(self.project_root, self.skills_registry, self.lock_manager, config),
        }
    
    def detect_environments(self) -> DetectionSummary:
        """Detect all AI coding agent environments."""
        return self.detector.detect_all()
    
    def plan_installation(self, targets: Optional[List[Target]] = None, 
                          scope: Scope = Scope.PROJECT,
                          auto: bool = False) -> InstallPlan:
        """Create installation plan based on detection and user selection."""
        detection = self.detect_environments()
        plan_targets = {}
        
        if auto:
            # Auto-install all detected targets with project config
            for target_name, result in detection.targets.items():
                target = Target(target_name)
                if result.project_config_detected:
                    caps = get_adapter_capabilities(target)
                    if (scope == Scope.PROJECT and caps.supports_project) or \
                       (scope == Scope.GLOBAL and caps.supports_global):
                        plan_targets[target] = scope
        elif targets:
            # Use explicitly specified targets
            for target in targets:
                caps = get_adapter_capabilities(target)
                if scope == Scope.PROJECT and caps.supports_project:
                    plan_targets[target] = scope
                elif scope == Scope.GLOBAL and caps.supports_global:
                    plan_targets[target] = scope
                else:
                    raise ValueError(f"Target {target} does not support scope {scope}")
        else:
            # Default: all detected with project config
            for target_name, result in detection.targets.items():
                target = Target(target_name)
                if result.project_config_detected:
                    caps = get_adapter_capabilities(target)
                    if caps.supports_project:
                        plan_targets[target] = scope
        
        return InstallPlan(targets=plan_targets, dry_run=self.config.dry_run)
    
    def execute_install(self, plan: InstallPlan) -> dict[Target, InstallResult]:
        """Execute installation according to plan."""
        results = {}
        
        for target, scope in plan.targets.items():
            adapter = self.adapters[target]
            result = adapter.install(scope=scope, dry_run=plan.dry_run)
            results[target] = result
            
            # Print result
            status = "PASS" if result.success else "FAIL"
            print(f"  {target.value}: {status} ({len(result.files_created)} files, {len(result.errors)} errors)")
            if result.errors:
                for err in result.errors:
                    print(f"    ERROR: {err}")
            if result.warnings:
                for warn in result.warnings:
                    print(f"    WARNING: {warn}")
        
        return results
    
    def run_sync(self, scope: Scope = Scope.PROJECT, 
                 targets: Optional[List[Target]] = None, 
                 dry_run: bool = False) -> dict[Target, any]:
        """Run sync across targets."""
        from python_skills.adapters.base import SyncResult
        
        if targets is None:
            # Sync all installed targets
            targets = list(self.lock_manager.get_all_targets().keys())
            targets = [Target(t) for t in targets if t in [t.value for t in Target]]
        
        results = {}
        for target in targets:
            if target not in self.adapters:
                continue
            adapter = self.adapters[target]
            result = adapter.sync(scope=scope, dry_run=dry_run)
            results[target] = result
            
            status = "PASS" if result.success else "FAIL"
            print(f"  {target.value}: {status} ({len(result.added)} added, {len(result.modified)} modified, {len(result.removed)} removed)")
            if result.errors:
                for err in result.errors:
                    print(f"    ERROR: {err}")
        
        return results
    
    def run_uninstall(self, scope: Scope = Scope.PROJECT,
                      targets: Optional[List[Target]] = None,
                      dry_run: bool = False) -> dict[Target, any]:
        """Run uninstall across targets."""
        from python_skills.adapters.base import UninstallResult
        
        if targets is None:
            targets = list(self.lock_manager.get_all_targets().keys())
            targets = [Target(t) for t in targets if t in [t.value for t in Target]]
        
        results = {}
        for target in targets:
            if target not in self.adapters:
                continue
            adapter = self.adapters[target]
            result = adapter.uninstall(scope=scope, dry_run=dry_run)
            results[target] = result
            
            status = "PASS" if result.success else "FAIL"
            print(f"  {target.value}: {status} ({len(result.files_removed)} files, {len(result.regions_removed)} regions)")
            if result.errors:
                for err in result.errors:
                    print(f"    ERROR: {err}")
            if result.warnings:
                for warn in result.warnings:
                    print(f"    WARNING: {warn}")
        
        return results
    
    def get_status(self, scope: Scope = Scope.PROJECT) -> dict[Target, any]:
        """Get installation status for all targets."""
        from python_skills.adapters.base import StatusResult
        
        results = {}
        for target_name, adapter in self.adapters.items():
            result = adapter.status(scope=scope)
            results[target_name] = result
            
            status = "Installed" if result.installed else "Not installed"
            print(f"  {target_name.value}: {status} ({len(result.files)} files)")
        
        return results