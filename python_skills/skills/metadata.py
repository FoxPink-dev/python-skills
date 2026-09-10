"""Skill metadata handling."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SkillMetadata:
    """Metadata for a skill from its SKILL.md frontmatter or .md file."""
    name: str
    category: str
    path: Path
    description: str = ""
    triggers: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    priority: str = "primary"
    estimated_tokens: int = 1500
    raw_frontmatter: dict = field(default_factory=dict)
    raw_content: str = ""

    @property
    def skill_name(self) -> str:
        """Get the skill name (directory or file stem)."""
        if self.path.is_file():
            return self.path.stem
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
    current_key = None
    current_list = None
    
    for line in frontmatter_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        
        # Check if this is a list item (starts with -)
        if stripped.startswith("- ") and current_key and current_list is not None:
            item = stripped[2:].strip().strip('"\'')
            current_list.append(item)
            continue
        
        # If we were building a list, save it
        if current_list is not None:
            frontmatter[current_key] = current_list
            current_list = None
            current_key = None
        
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            
            # Handle inline lists [item1, item2]
            if value.startswith("[") and value.endswith("]"):
                value = [v.strip().strip('"\'') for v in value[1:-1].split(",")]
                frontmatter[key] = value
            # Handle empty value (might be start of multi-line list)
            elif not value:
                current_key = key
                current_list = []
            else:
                frontmatter[key] = value

    # Save any pending list
    if current_list is not None:
        frontmatter[current_key] = current_list

    return frontmatter, remaining


def _extract_description_from_content(content: str) -> str:
    """Extract a description from markdown content without frontmatter.
    
    Looks for patterns like:
    - **Purpose**: ...
    - # Title\n\nDescription
    - First paragraph
    """
    lines = content.strip().split("\n")

    for line in lines:
        line = line.strip()
        # Look for **Purpose**: pattern
        if line.lower().startswith("**purpose**:"):
            return line.split(":", 1)[1].strip()
        # Look for **When to use**: pattern
        if line.lower().startswith("**when to use**:"):
            return line.split(":", 1)[1].strip()

    # Use first heading + next non-empty line
    found_heading = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            found_heading = True
            continue
        if found_heading and line:
            return line[:200]

    return ""


def load_skill_metadata(skill_path: Path) -> SkillMetadata | None:
    """Load metadata from a skill path.
    
    Supports two formats:
    1. Flat file: skills/<category>/<name>.md
    2. Agent Skills: skills/<category>/<name>/SKILL.md
    """
    # Determine the actual skill file and content
    if skill_path.is_file() and skill_path.suffix == ".md":
        # Flat file format
        content = skill_path.read_text(encoding="utf-8")
        skill_name = skill_path.stem
        skill_file = skill_path
    elif skill_path.is_dir():
        # Agent Skills format
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            return None
        content = skill_file.read_text(encoding="utf-8")
        skill_name = skill_path.name
    else:
        return None

    frontmatter, content_body = parse_skill_frontmatter(content)

    # Determine category from path
    # For flat files: parent is the category
    # For directories: grandparent is the category
    if skill_path.is_file():
        category = skill_path.parent.name
    else:
        category = skill_path.parent.name

    from .loader import SkillLoader
    if category not in SkillLoader.CATEGORIES:
        category = "core"

    # Get description from frontmatter or extract from content
    description = frontmatter.get("description", "")
    if not description:
        description = _extract_description_from_content(content)

    return SkillMetadata(
        name=skill_name,
        category=category,
        path=skill_path,
        description=description,
        triggers=frontmatter.get("triggers", []) if isinstance(frontmatter.get("triggers"), list) else [],
        dependencies=frontmatter.get("dependencies", []) if isinstance(frontmatter.get("dependencies"), list) else [],
        related=frontmatter.get("related", []) if isinstance(frontmatter.get("related"), list) else [],
        priority=frontmatter.get("priority", "primary"),
        estimated_tokens=frontmatter.get("estimated_tokens", 1500) if isinstance(frontmatter.get("estimated_tokens"), int) else 1500,
        raw_frontmatter=frontmatter,
        raw_content=content_body,
    )
