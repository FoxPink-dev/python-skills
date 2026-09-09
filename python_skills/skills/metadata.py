"""Skill metadata handling."""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SkillMetadata:
    """Metadata for a skill from its SKILL.md frontmatter."""
    name: str
    category: str
    path: Path
    description: str = ""
    triggers: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    priority: str = "primary"
    estimated_tokens: int = 1500
    raw_frontmatter: dict = field(default_factory=dict)
    raw_content: str = ""
    
    @property
    def skill_name(self) -> str:
        """Get the skill name (directory name)."""
        return self.path.name


def parse_skill_frontmatter(content: str) -> tuple[dict, str]:
    """
    Parse YAML frontmatter from skill content.
    
    Returns:
        Tuple of (frontmatter_dict, remaining_content)
    """
    if not content.startswith("---"):
        return {}, content
    
    # Find the closing ---
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return {}, content
    
    frontmatter_text = content[3:end_idx].strip()
    remaining = content[end_idx + 3:].lstrip()
    
    # Simple YAML parsing for our needs
    frontmatter = {}
    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            # Handle lists
            if value.startswith("[") and value.endswith("]"):
                value = [v.strip().strip('"\'') for v in value[1:-1].split(",")]
            frontmatter[key] = value
    
    return frontmatter, remaining


def load_skill_metadata(skill_path: Path) -> Optional[SkillMetadata]:
    """Load metadata from a skill directory."""
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        return None
    
    content = skill_file.read_text(encoding="utf-8")
    frontmatter, content_body = parse_skill_frontmatter(content)
    
    # Determine category from path
    category = skill_path.parent.name
    if category not in [
        "core", "stdlib", "generation", "engineering", 
        "quality", "security", "testing", "refactoring", 
        "debugging", "anti_patterns"
    ]:
        category = "core"
    
    return SkillMetadata(
        name=skill_path.name,
        category=category,
        path=skill_path,
        description=frontmatter.get("description", ""),
        triggers=frontmatter.get("triggers", []) if isinstance(frontmatter.get("triggers"), list) else [],
        dependencies=frontmatter.get("dependencies", []) if isinstance(frontmatter.get("dependencies"), list) else [],
        priority=frontmatter.get("priority", "primary"),
        estimated_tokens=frontmatter.get("estimated_tokens", 1500) if isinstance(frontmatter.get("estimated_tokens"), int) else 1500,
        raw_frontmatter=frontmatter,
        raw_content=content_body,
    )