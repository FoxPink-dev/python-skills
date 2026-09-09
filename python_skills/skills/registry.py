"""Skill registry - central skill discovery and management."""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from .loader import SkillLoader
from .metadata import SkillMetadata, load_skill_metadata


@dataclass
class SkillRegistry:
    """Registry of all available skills."""
    skills_root: Path
    loader: SkillLoader = field(init=False)
    _skills: dict[str, SkillMetadata] = field(default_factory=dict)
    _by_category: dict[str, list[SkillMetadata]] = field(default_factory=dict)
    _loaded: bool = False
    
    def __post_init__(self):
        self.loader = SkillLoader(self.skills_root)
    
    def load_all(self) -> dict[str, SkillMetadata]:
        """Load all skills into registry."""
        if self._loaded:
            return self._skills
        
        self._skills = {}
        self._by_category = {}
        
        for skill_name in self.loader.get_all_skill_names():
            metadata = self.loader.load_skill(skill_name)
            if metadata:
                self._skills[skill_name] = metadata
                if metadata.category not in self._by_category:
                    self._by_category[metadata.category] = []
                self._by_category[metadata.category].append(metadata)
        
        self._loaded = True
        return self._skills
    
    def get_skill(self, name: str) -> Optional[SkillMetadata]:
        """Get a skill by name."""
        if not self._loaded:
            self.load_all()
        return self._skills.get(name)
    
    def get_skills_by_category(self, category: str) -> list[SkillMetadata]:
        """Get all skills in a category."""
        if not self._loaded:
            self.load_all()
        return self._by_category.get(category, [])
    
    def get_all_skills(self) -> list[SkillMetadata]:
        """Get all skills as a list."""
        if not self._loaded:
            self.load_all()
        return list(self._skills.values())
    
    def get_skill_names(self) -> list[str]:
        """Get all skill names."""
        if not self._loaded:
            self.load_all()
        return list(self._skills.keys())
    
    def get_categories(self) -> list[str]:
        """Get all categories."""
        if not self._loaded:
            self.load_all()
        return list(self._by_category.keys())
    
    def get_skill_content(self, name: str) -> Optional[str]:
        """Get raw SKILL.md content for a skill."""
        return self.loader.get_skill_content(name)
    
    @property
    def count(self) -> int:
        if not self._loaded:
            self.load_all()
        return len(self._skills)


# Global registry instance
_registry: Optional[SkillRegistry] = None


def get_registry(skills_root: Optional[Path] = None) -> SkillRegistry:
    """Get or create the global skill registry."""
    global _registry
    if _registry is None:
        if skills_root is None:
            # Try to find skills directory relative to this file
            current = Path(__file__).resolve().parent.parent.parent
            skills_root = current / "skills"
        _registry = SkillRegistry(skills_root)
    return _registry


def reset_registry() -> None:
    """Reset the global registry (for testing)."""
    global _registry
    _registry = None