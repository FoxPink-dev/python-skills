"""Manifest and version management for python-skills."""

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import importlib.metadata


@dataclass
class SkillManifestEntry:
    """Entry for a skill in the manifest."""
    name: str
    category: str
    path: str
    description: str = ""


@dataclass
class Manifest:
    """Python Skills manifest."""
    name: str = "python-skills"
    version: str = "1.0.0"
    skill_count: int = 69
    categories: int = 10
    categories_list: list[str] = None
    targets: list[str] = None
    schema_version: int = 1
    built_at: str = ""
    
    def __post_init__(self):
        if self.categories_list is None:
            self.categories_list = [
                "core", "stdlib", "generation", "engineering", 
                "quality", "security", "testing", "refactoring", 
                "debugging", "anti_patterns"
            ]
        if self.targets is None:
            self.targets = ["claude", "cursor", "kiro", "cline", "universal"]
        if not self.built_at:
            self.built_at = datetime.utcnow().isoformat() + "Z"


def get_version() -> str:
    """Get the version from pyproject.toml via importlib.metadata."""
    try:
        return importlib.metadata.version("python-skills")
    except importlib.metadata.PackageNotFoundError:
        # Fallback: read from pyproject.toml
        pyproject_path = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            import tomllib
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "1.0.0")
        return "1.0.0"


def get_manifest() -> Manifest:
    """Get the current manifest with version info."""
    version = get_version()
    return Manifest(version=version)


def write_manifest(output_path: Path) -> None:
    """Write manifest to a JSON file."""
    manifest = get_manifest()
    output_path.write_text(json.dumps(asdict(manifest), indent=2))