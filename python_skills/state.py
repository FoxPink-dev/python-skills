"""Installation state and lock file management."""

import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional
import hashlib


@dataclass
class FileRecord:
    """Record of a managed file."""
    path: str
    hash: str
    size: int
    region_hash: Optional[str] = None  # For AGENTS.md managed section


@dataclass
class TargetState:
    """State for a single target."""
    scope: str
    status: str = "installed"
    files: list[FileRecord] = field(default_factory=list)


@dataclass
class LockState:
    """Complete lock state for python-skills installation."""
    version: str = "1.0.0"
    schema_version: int = 1
    installed_at: str = ""
    updated_at: str = ""
    canonical_skills_hash: str = ""
    targets: dict[str, TargetState] = field(default_factory=dict)
    skill_count: int = 69
    adapter_version: str = "1.0.0"

    def __post_init__(self):
        if not self.installed_at:
            self.installed_at = datetime.utcnow().isoformat() + "Z"
        if not self.updated_at:
            self.updated_at = datetime.utcnow().isoformat() + "Z"


class LockManager:
    """Manages the lock file for python-skills installation state."""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root).resolve()
        self.lock_dir = self.project_root / ".python-skills"
        self.lock_file = self.lock_dir / "lock.json"
        self._lock: Optional[LockState] = None
    
    def _compute_file_hash(self, path: Path) -> str:
        """Compute SHA256 hash of a file."""
        hasher = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _compute_region_hash(self, path: Path, start_marker: str, end_marker: str) -> Optional[str]:
        """Compute hash of content between markers."""
        try:
            content = path.read_text(encoding="utf-8")
            start_idx = content.find(start_marker)
            end_idx = content.find(end_marker)
            if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
                return None
            region_content = content[start_idx + len(start_marker):end_idx]
            return hashlib.sha256(region_content.encode("utf-8")).hexdigest()
        except Exception:
            return None
    
    def _compute_skills_hash(self, skills_root: Path) -> str:
        """Compute combined hash of all canonical skills."""
        hasher = hashlib.sha256()
        skill_dirs = sorted([d for d in skills_root.iterdir() if d.is_dir()])
        for skill_dir in skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                hasher.update(skill_file.read_bytes())
        return hasher.hexdigest()
    
    def load(self) -> LockState:
        """Load lock state from file."""
        if self._lock is not None:
            return self._lock
        
        if self.lock_file.exists():
            try:
                data = json.loads(self.lock_file.read_text(encoding="utf-8"))
                self._lock = LockState(**data)
                return self._lock
            except Exception:
                pass
        
        # Return empty lock state
        self._lock = LockState()
        return self._lock
    
    def save(self, lock: Optional[LockState] = None) -> None:
        """Save lock state to file."""
        if lock is not None:
            self._lock = lock
        if self._lock is None:
            self._lock = LockState()
        
        self._lock.updated_at = datetime.utcnow().isoformat() + "Z"
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file.write_text(json.dumps(asdict(self._lock), indent=2), encoding="utf-8")
    
    def get_state(self) -> LockState:
        """Get current lock state."""
        return self.load()
    
    def record_file(self, target: str, scope: str, path: Path, region_markers: tuple[str, str] = None) -> None:
        """Record a managed file in the lock state."""
        lock = self.load()
        
        if target not in lock.targets:
            lock.targets[target] = TargetState(scope=scope)
        elif lock.targets[target].scope != scope:
            # Scope changed - treat as new
            lock.targets[target] = TargetState(scope=scope)
        
        target_state = lock.targets[target]
        
        # Compute file hash
        file_hash = self._compute_file_hash(path)
        file_size = path.stat().st_size
        
        # Compute region hash if markers provided
        region_hash = None
        if region_markers:
            region_hash = self._compute_region_hash(path, region_markers[0], region_markers[1])
        
        # Check if file already recorded
        existing = next((f for f in target_state.files if f.path == str(path.relative_to(self.project_root))), None)
        if existing:
            existing.hash = file_hash
            existing.size = file_size
            existing.region_hash = region_hash
        else:
            target_state.files.append(FileRecord(
                path=str(path.relative_to(self.project_root)),
                hash=file_hash,
                size=file_size,
                region_hash=region_hash
            ))
        
        self.save(lock)
    
    def remove_file(self, target: str, path: Path) -> bool:
        """Remove a file record from lock state. Returns True if removed."""
        lock = self.load()
        
        if target not in lock.targets:
            return False
        
        target_state = lock.targets[target]
        rel_path = str(path.relative_to(self.project_root))
        
        for i, f in enumerate(target_state.files):
            if f.path == rel_path:
                target_state.files.pop(i)
                self.save(lock)
                return True
        
        return False
    
    def get_managed_files(self, target: str, scope: str) -> list[FileRecord]:
        """Get all managed files for a target and scope."""
        lock = self.load()
        if target not in lock.targets:
            return []
        if lock.targets[target].scope != scope:
            return []
        return lock.targets[target].files
    
    def get_target_status(self, target: str) -> Optional[TargetState]:
        """Get status for a target."""
        lock = self.load()
        return lock.targets.get(target)
    
    def update_canonical_hash(self, skills_root: Path) -> None:
        """Update the canonical skills hash."""
        lock = self.load()
        lock.canonical_skills_hash = self._compute_skills_hash(skills_root)
        self.save(lock)
    
    def get_all_targets(self) -> dict[str, TargetState]:
        """Get all target states."""
        return self.load().targets