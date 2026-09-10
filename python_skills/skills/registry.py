"""Skill registry - central skill discovery and management."""

from dataclasses import dataclass, field
from pathlib import Path

from .loader import SkillLoader
from .metadata import SkillMetadata


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

    def get_skill(self, name: str) -> SkillMetadata | None:
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

    def get_skill_content(self, name: str) -> str | None:
        """Get raw SKILL.md content for a skill."""
        return self.loader.get_skill_content(name)

    def get_related_skills(self, name: str) -> list[SkillMetadata]:
        """Get skills related to the given skill."""
        if not self._loaded:
            self.load_all()
        skill = self._skills.get(name)
        if not skill:
            return []
        related = []
        for rel_name in skill.related:
            # Try exact match first
            rel_skill = self._skills.get(rel_name)
            if rel_skill:
                related.append(rel_skill)
                continue
            # Try extracting just the skill name (after last /)
            if "/" in rel_name:
                short_name = rel_name.rsplit("/", 1)[-1]
                rel_skill = self._skills.get(short_name)
                if rel_skill:
                    related.append(rel_skill)
        return related

    def find_composition(self, task_description: str) -> list[SkillMetadata]:
        """Find skills relevant to a task based on triggers and keywords.
        
        Returns a list of skills sorted by relevance (most relevant first).
        """
        if not self._loaded:
            self.load_all()
        
        task_lower = task_description.lower()
        scored: list[tuple[int, SkillMetadata]] = []
        
        for skill in self._skills.values():
            score = 0
            # Check triggers
            for trigger in skill.triggers:
                if trigger.lower() in task_lower:
                    score += 3
            # Check name
            if skill.name.lower() in task_lower:
                score += 5
            # Check category
            if skill.category.lower() in task_lower:
                score += 2
            # Check description keywords
            desc_words = skill.description.lower().split()
            for word in desc_words:
                if len(word) > 3 and word in task_lower:
                    score += 1
            
            if score > 0:
                scored.append((score, skill))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [skill for _, skill in scored]

    @property
    def count(self) -> int:
        if not self._loaded:
            self.load_all()
        return len(self._skills)


# Global registry instance
_registry: SkillRegistry | None = None


def get_registry(skills_root: Path | None = None) -> SkillRegistry:
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
