"""Skill loading utilities."""

from pathlib import Path

from .metadata import SkillMetadata, load_skill_metadata


class SkillLoader:
    """Loads skills from the canonical skills directory.
    
    Supports two directory layouts:
    1. Flat files: skills/<category>/<skill-name>.md  (current canonical)
    2. Agent Skills: skills/<category>/<skill-name>/SKILL.md  (Agent Skills spec)
    """

    CATEGORIES = frozenset([
        "core", "stdlib", "generation", "engineering",
        "quality", "security", "testing", "refactoring",
        "debugging", "anti_patterns",
    ])

    def __init__(self, skills_root: Path):
        self.skills_root = Path(skills_root).resolve()

    def _is_category_dir(self, path: Path) -> bool:
        """Check if a directory is a valid skill category."""
        return path.is_dir() and path.name in self.CATEGORIES

    def _discover_skills_in_category(self, category_path: Path) -> list[Path]:
        """Discover skill paths in a category directory.
        
        Returns list of Paths, each pointing to either:
        - A .md file (flat format)
        - A directory containing SKILL.md (Agent Skills format)
        """
        skills = []
        if not category_path.is_dir():
            return skills

        for item in category_path.iterdir():
            if item.is_file() and item.suffix == ".md" and item.stem != "README":
                skills.append(item)
            elif item.is_dir() and (item / "SKILL.md").exists():
                skills.append(item)

        return skills

    def _discover_root_skills(self) -> list[Path]:
        """Discover skill .md files at the skills/ root (e.g., core skills)."""
        skills = []
        for item in self.skills_root.iterdir():
            if item.is_file() and item.suffix == ".md" and item.stem != "README":
                skills.append(item)
        return skills

    def load_skill(self, skill_name: str) -> SkillMetadata | None:
        """Load a single skill by name."""
        # Check root-level flat files first (core skills)
        root_path = self.skills_root / f"{skill_name}.md"
        if root_path.is_file():
            return load_skill_metadata(root_path)

        for category_dir in self.skills_root.iterdir():
            if not self._is_category_dir(category_dir):
                continue

            # Check flat file format: <name>.md
            flat_path = category_dir / f"{skill_name}.md"
            if flat_path.is_file():
                return load_skill_metadata(flat_path)

            # Check Agent Skills format: <name>/SKILL.md
            dir_path = category_dir / skill_name
            if dir_path.is_dir():
                return load_skill_metadata(dir_path)

        return None

    def load_category(self, category: str) -> list:
        """Load all skills in a category."""
        category_path = self.skills_root / category
        if not self._is_category_dir(category_path):
            return []

        skills = []
        for skill_path in self._discover_skills_in_category(category_path):
            metadata = load_skill_metadata(skill_path)
            if metadata:
                skills.append(metadata)
        return skills

    def load_all_skills(self) -> list:
        """Load all skills from all categories and root."""
        skills = []

        # Load root-level skills (core)
        for skill_path in self._discover_root_skills():
            metadata = load_skill_metadata(skill_path)
            if metadata:
                skills.append(metadata)

        # Load category skills
        for category_dir in self.skills_root.iterdir():
            if self._is_category_dir(category_dir):
                for skill_path in self._discover_skills_in_category(category_dir):
                    metadata = load_skill_metadata(skill_path)
                    if metadata:
                        skills.append(metadata)
        return skills

    def get_skill_content(self, skill_name: str) -> str | None:
        """Get the raw content of a skill."""
        # Check root-level first
        root_path = self.skills_root / f"{skill_name}.md"
        if root_path.is_file():
            return root_path.read_text(encoding="utf-8")

        for category_dir in self.skills_root.iterdir():
            if not self._is_category_dir(category_dir):
                continue

            # Flat format
            flat_path = category_dir / f"{skill_name}.md"
            if flat_path.is_file():
                return flat_path.read_text(encoding="utf-8")

            # Agent Skills format
            dir_path = category_dir / skill_name / "SKILL.md"
            if dir_path.exists():
                return dir_path.read_text(encoding="utf-8")

        return None

    def get_skill_path(self, skill_name: str) -> Path | None:
        """Get the filesystem path of a skill."""
        # Check root-level first
        root_path = self.skills_root / f"{skill_name}.md"
        if root_path.is_file():
            return root_path

        for category_dir in self.skills_root.iterdir():
            if not self._is_category_dir(category_dir):
                continue

            flat_path = category_dir / f"{skill_name}.md"
            if flat_path.is_file():
                return flat_path

            dir_path = category_dir / skill_name / "SKILL.md"
            if dir_path.exists():
                return dir_path

        return None

    def get_all_skill_names(self) -> list[str]:
        """Get list of all skill names."""
        names = []

        # Root-level skills
        for skill_path in self._discover_root_skills():
            names.append(skill_path.stem)

        # Category skills
        for category_dir in self.skills_root.iterdir():
            if self._is_category_dir(category_dir):
                for skill_path in self._discover_skills_in_category(category_dir):
                    if skill_path.is_file():
                        names.append(skill_path.stem)
                    elif skill_path.is_dir():
                        names.append(skill_path.name)
        return sorted(names)
