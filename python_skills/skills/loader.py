"""Skill loading utilities."""

from pathlib import Path
from typing import Optional
from .metadata import load_skill_metadata, SkillMetadata


class SkillLoader:
    """Loads skills from the canonical skills directory."""
    
    def __init__(self, skills_root: Path):
        self.skills_root = Path(skills_root).resolve()
    
    def load_skill(self, skill_name: str) -> Optional[SkillMetadata]:
        """Load a single skill by name."""
        # Search in all categories
        for category_dir in self.skills_root.iterdir():
            if not category_dir.is_dir():
                continue
            skill_path = category_dir / skill_name
            if skill_path.is_dir():
                return load_skill_metadata(skill_path)
        return None
    
    def load_category(self, category: str) -> list:
        """Load all skills in a category."""
        category_path = self.skills_root / category
        if not category_path.is_dir():
            return []
        
        skills = []
        for skill_dir in category_path.iterdir():
            if skill_dir.is_dir():
                metadata = load_skill_metadata(skill_dir)
                if metadata:
                    skills.append(metadata)
        return skills
    
    def load_all_skills(self) -> list:
        """Load all skills from all categories."""
        skills = []
        for category_dir in self.skills_root.iterdir():
            if category_dir.is_dir():
                for skill_dir in category_dir.iterdir():
                    if skill_dir.is_dir():
                        metadata = load_skill_metadata(skill_dir)
                        if metadata:
                            skills.append(metadata)
        return skills
    
    def get_skill_content(self, skill_name: str) -> Optional[str]:
        """Get the raw content of a skill's SKILL.md."""
        for category_dir in self.skills_root.iterdir():
            if not category_dir.is_dir():
                continue
            skill_path = category_dir / skill_name / "SKILL.md"
            if skill_path.exists():
                return skill_path.read_text(encoding="utf-8")
        return None
    
    def get_all_skill_names(self) -> list[str]:
        """Get list of all skill names."""
        names = []
        for category_dir in self.skills_root.iterdir():
            if category_dir.is_dir():
                for skill_dir in category_dir.iterdir():
                    if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                        names.append(skill_dir.name)
        return sorted(names)