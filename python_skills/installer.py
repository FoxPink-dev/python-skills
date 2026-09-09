"""Installer orchestration for python-skills."""

from dataclasses import dataclass
from pathlib import Path

from python_skills.adapters import get_adapter
from python_skills.adapters.base import InstallResult
from python_skills.config import InstallConfig, Scope, Target, get_adapter_capabilities
from python_skills.detector import DetectionSummary, EnvironmentDetector
from python_skills.skills.registry import get_registry
from python_skills.state import LockManager


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

    def detect_environments(self) -> DetectionSummary:
        """Detect all AI coding agent environments."""
        return self.detector.detect_all()

    def plan_installation(self, targets: list[Target] | None = None,
                          scope: Scope = Scope.PROJECT,
                          auto: bool = False) -> InstallPlan:
        """Create installation plan based on detection and user selection."""
        detection = self.detect_environments()
        plan_targets = {}

        if auto:
            for target_name, result in detection.targets.items():
                target = Target(target_name)
                caps = get_adapter_capabilities(target)
                if result.project_config_detected or result.application_detected:
                    if (scope == Scope.PROJECT and caps.supports_project) or \
                       (scope == Scope.GLOBAL and caps.supports_global):
                        plan_targets[target] = scope
        elif targets:
            for target in targets:
                caps = get_adapter_capabilities(target)
                if scope == Scope.PROJECT and caps.supports_project:
                    plan_targets[target] = scope
                elif scope == Scope.GLOBAL and caps.supports_global:
                    plan_targets[target] = scope
                else:
                    raise ValueError(f"Target {target} does not support scope {scope}")
        else:
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
            try:
                adapter = get_adapter(target, self.project_root, self.skills_registry, self.lock_manager, self.config)
                result = adapter.install(scope=scope.value, dry_run=plan.dry_run)
                results[target] = result

                status = "PASS" if result.success else "FAIL"
                print(f"  {target.value}: {status} ({len(result.files_created)} files, {len(result.errors)} errors)")
                if result.errors:
                    for err in result.errors:
                        print(f"    ERROR: {err}")
                if result.warnings:
                    for warn in result.warnings:
                        print(f"    WARNING: {warn}")
            except Exception as e:
                results[target] = InstallResult(
                    success=False, target=target.value, scope=scope.value,
                    errors=[str(e)]
                )
                print(f"  {target.value}: FAIL ({e})")

        return results

    def run_sync(self, scope: Scope = Scope.PROJECT,
                 targets: list[Target] | None = None,
                 dry_run: bool = False) -> dict[Target, any]:
        """Run sync across targets."""

        if targets is None:
            targets = [Target(t) for t in self.lock_manager.get_all_targets().keys()
                       if t in [t.value for t in Target]]

        results = {}
        for target in targets:
            try:
                adapter = get_adapter(target, self.project_root, self.skills_registry, self.lock_manager, self.config)
                result = adapter.sync(scope=scope.value, dry_run=dry_run)
                results[target] = result

                status = "PASS" if result.success else "FAIL"
                print(f"  {target.value}: {status} ({len(result.added)} added, {len(result.modified)} modified, {len(result.removed)} removed)")
                if result.errors:
                    for err in result.errors:
                        print(f"    ERROR: {err}")
            except Exception as e:
                print(f"  {target.value}: FAIL ({e})")

        return results

    def run_uninstall(self, scope: Scope = Scope.PROJECT,
                      targets: list[Target] | None = None,
                      dry_run: bool = False) -> dict[Target, any]:
        """Run uninstall across targets."""

        if targets is None:
            targets = [Target(t) for t in self.lock_manager.get_all_targets().keys()
                       if t in [t.value for t in Target]]

        results = {}
        for target in targets:
            try:
                adapter = get_adapter(target, self.project_root, self.skills_registry, self.lock_manager, self.config)
                result = adapter.uninstall(scope=scope.value, dry_run=dry_run)
                results[target] = result

                status = "PASS" if result.success else "FAIL"
                print(f"  {target.value}: {status} ({len(result.files_removed)} files)")
                if result.errors:
                    for err in result.errors:
                        print(f"    ERROR: {err}")
            except Exception as e:
                print(f"  {target.value}: FAIL ({e})")

        return results

    def get_status(self, scope: Scope = Scope.PROJECT) -> dict[Target, any]:
        """Get installation status for all targets."""

        results = {}
        for target in Target:
            try:
                adapter = get_adapter(target, self.project_root, self.skills_registry, self.lock_manager, self.config)
                result = adapter.status(scope=scope.value)
                results[target] = result

                status = "Installed" if result.installed else "Not installed"
                print(f"  {target.value}: {status} ({len(result.files)} files)")
            except Exception as e:
                print(f"  {target.value}: Error ({e})")

        return results
