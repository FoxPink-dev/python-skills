"""Add frontmatter to all skills without it."""
import json
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parent / "skills"


def get_triggers_for_skill(name: str, category: str) -> list[str]:
    """Generate appropriate triggers based on skill name and category."""
    trigger_map = {
        "advanced_python": ["advanced", "python", "patterns", "advanced python"],
        "index": ["anti-patterns", "bad practice", "smell"],
        "comprehensions": ["list comprehension", "dict comprehension", "comprehension"],
        "control_flow": ["if", "else", "match", "control flow", "branch"],
        "data_structures": ["list", "dict", "set", "tuple", "data structure"],
        "common_bugs": ["bug", "common mistake", "debugging", "error"],
        "inspection_techniques": ["inspect", "debug", "inspection", "examine"],
        "root_cause": ["root cause", "analyze", "investigate", "debugging"],
        "application_logging": ["logging", "log", "logger", "audit"],
        "cli_apps": ["cli", "command line", "argparse", "click"],
        "configuration": ["config", "configuration", "settings", "environment"],
        "dependency_management": ["dependencies", "pip", "poetry", "requirements"],
        "modules_packages": ["module", "package", "import", "__init__"],
        "packaging": ["packaging", "wheel", "sdist", "pyproject"],
        "project_structure": ["project structure", "directory", "layout"],
        "pyproject_toml": ["pyproject.toml", "build", "hatch", "setuptools"],
        "virtual_environments": ["venv", "virtual environment", "conda", "poetry"],
        "protocols_generics": ["protocol", "generic", "typing", "type"],
        "type_hints": ["type hint", "typing", "annotation", "type"],
        "validation_pipeline": ["validation", "pipeline", "validate", "schema"],
        "workflow": ["workflow", "pipeline", "ci", "cd"],
        "oop": ["class", "object", "inheritance", "polymorphism"],
        "abstractions": ["abstraction", "interface", "abstract", "design"],
        "comments": ["comment", "docstring", "documentation"],
        "documentation": ["documentation", "readme", "docs"],
        "duplication": ["duplication", "dry", "code reuse", "duplicate"],
        "maintainability": ["maintainability", "maintenance", "refactor"],
        "naming": ["naming", "variable name", "function name", "convention"],
        "quality_functions": ["function", "quality", "pure function", "side effect"],
        "readability": ["readability", "readable", "clarity", "clean code"],
        "type_annotations": ["type annotation", "typing", "type hint", "annotation"],
        "behavior_preservation": ["behavior", "preserve", "maintain", "refactoring"],
        "incremental": ["incremental", "step", "gradual", "refactoring"],
        "interface_stability": ["interface", "stability", "api", "breaking change"],
        "safe_refactoring": ["refactoring", "safe", "test coverage", "regression"],
        "auth_boundaries": ["authentication", "authorization", "auth", "security"],
        "command_injection": ["command injection", "subprocess", "shell", "injection"],
        "dependency_risks": ["dependency", "supply chain", "risk", "vulnerability"],
        "secrets": ["secret", "api key", "credential", "env"],
        "unsafe_deserialization": ["deserialization", "pickle", "yaml", "unsafe"],
        "argparse": ["argparse", "argument parser", "cli"],
        "collections": ["collections", "deque", "Counter", "defaultdict"],
        "datetime": ["datetime", "date", "time", "timedelta"],
        "functools": ["functools", "lru_cache", "partial", "wraps"],
        "itertools": ["itertools", "chain", "combinations", "permutations"],
        "json": ["json", "serialization", "json.load", "json.dump"],
        "logging": ["logging", "logger", "debug", "info", "warning"],
        "os_sys": ["os", "sys", "platform", "filesystem"],
        "pathlib": ["pathlib", "Path", "file path", "directory"],
        "re": ["regex", "regular expression", "pattern", "match"],
        "statistics": ["statistics", "mean", "median", "stdev"],
        "subprocess": ["subprocess", "shell", "process", "command"],
        "coverage": ["coverage", "pytest-cov", "code coverage", "coverage report"],
        "fixtures_mocks": ["fixture", "mock", "pytest", "monkeypatch"],
        "organization": ["test organization", "test structure", "pytest", "test suite"],
        "parameterized": ["parameterized", "parametrize", "pytest.mark.parametrize"],
        "variables_types": ["variable", "type", "int", "str", "bool"],
    }
    return trigger_map.get(name, [name, category])


def get_priority_for_skill(category: str) -> str:
    """Get priority based on category."""
    if category == "security":
        return "critical"
    if category in ("core", "generation"):
        return "primary"
    return "supporting"


def add_frontmatter_to_file(skill_path: Path, name: str, category: str) -> bool:
    """Add frontmatter to a skill file."""
    content = skill_path.read_text(encoding="utf-8")

    # Skip if already has frontmatter
    if content.startswith("---"):
        return False

    # Extract purpose
    purpose = ""
    for line in content.split("\n"):
        line = line.strip()
        if "**Purpose**:" in line:
            purpose = line.split("**Purpose**:")[1].strip()
            break
    if not purpose:
        # Use first heading description
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("# ") and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not next_line.startswith("#"):
                    purpose = next_line[:100]
                    break
    if not purpose:
        purpose = f"{name} patterns and best practices"

    # Get triggers
    triggers = get_triggers_for_skill(name, category)

    # Get priority
    priority = get_priority_for_skill(category)

    # Estimate tokens based on file size
    estimated_tokens = max(1000, min(3000, len(content) // 3))

    # Build frontmatter
    triggers_yaml = "\n".join(f"  - {t}" for t in triggers)
    frontmatter = f"""---
name: {name}
purpose: {purpose}
category: {category}
triggers:
{triggers_yaml}
dependencies: []
related: []
priority: {priority}
estimated_tokens: {estimated_tokens}
---
"""
    # Add frontmatter before existing content
    skill_path.write_text(frontmatter + content, encoding="utf-8")
    return True


def add_related_to_functions():
    """Add related field to functions.md if missing."""
    functions_path = SKILLS_ROOT / "functions.md"
    if not functions_path.exists():
        return False

    content = functions_path.read_text(encoding="utf-8")
    if "related:" not in content.split("---")[1] if "---" in content else "":
        # Add related field after dependencies
        lines = content.split("\n")
        new_lines = []
        in_deps = False
        deps_done = False
        for line in lines:
            new_lines.append(line)
            if line.startswith("dependencies:"):
                in_deps = True
            elif in_deps and not line.startswith("  -") and not line.startswith("dependencies"):
                # End of dependencies section
                in_deps = False
                if not deps_done:
                    # Insert related field
                    new_lines.insert(-1, "related: []")
                    deps_done = True
        functions_path.write_text("\n".join(new_lines), encoding="utf-8")
        return True
    return False


def main():
    # Find all skills without frontmatter
    skills_with_no_frontmatter = []
    for md_file in SKILLS_ROOT.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        if not content.startswith("---"):
            rel_path = md_file.relative_to(SKILLS_ROOT)
            parts = rel_path.parts
            if len(parts) >= 2:
                category = parts[-2]
                name = md_file.stem
            else:
                category = "core"
                name = md_file.stem
            skills_with_no_frontmatter.append((md_file, name, category))

    print(f"Found {len(skills_with_no_frontmatter)} skills without frontmatter")

    # Add frontmatter to each
    added = 0
    for skill_path, name, category in skills_with_no_frontmatter:
        if add_frontmatter_to_file(skill_path, name, category):
            added += 1
            print(f"  Added frontmatter to {name} ({category})")

    # Add related to functions.md
    if add_related_to_functions():
        print("  Added related field to functions.md")

    print(f"\nDone. Added frontmatter to {added} skills.")

    # Verify
    total_with_frontmatter = 0
    for md_file in SKILLS_ROOT.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        if content.startswith("---"):
            total_with_frontmatter += 1
    print(f"Total skills with frontmatter: {total_with_frontmatter}")


if __name__ == "__main__":
    main()
