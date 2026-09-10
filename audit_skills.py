"""Audit all skill .md files under skills/ and produce a JSON report."""

import json
import sys
from pathlib import Path

# Add parent so we can import the existing parser
sys.path.insert(0, str(Path(__file__).resolve().parent))
from python_skills.skills.metadata import parse_skill_frontmatter

SKILLS_ROOT = Path(__file__).resolve().parent / "skills"
OUTPUT = Path(__file__).resolve().parent / "skills_audit.json"

CATEGORIES = frozenset([
    "core", "stdlib", "generation", "engineering",
    "quality", "security", "testing", "refactoring",
    "debugging", "anti_patterns",
])


def discover_skill_files(root: Path) -> list[Path]:
    """Return all .md files under root, recursively."""
    return sorted(root.rglob("*.md"))


def parent_dir_name(skill_file: Path) -> str:
    """Return the immediate parent directory name."""
    return skill_file.parent.name


def resolve_ref_path(skill_file: Path, ref: str, root: Path) -> bool:
    """Check whether a dependency/related reference resolves to an existing .md file.

    References come in two flavours:
      - "testing/edge_cases.md"  (with .md)
      - "testing/edge_cases"     (without .md)
    Both should map to a real file under skills/.
    """
    # Try as-is first (relative to skills root)
    candidate = root / ref
    if candidate.is_file():
        return True
    # Try appending .md
    if not ref.endswith(".md"):
        candidate = root / (ref + ".md")
        if candidate.is_file():
            return True
    return False


def audit() -> dict:
    files = discover_skill_files(SKILLS_ROOT)

    all_skills = []
    skills_with_frontmatter = 0
    skills_without_frontmatter = 0
    invalid_references = []
    name_mismatches = []
    category_mismatches = []
    missing_fields = []
    trigger_map: dict[str, list[str]] = {}

    for f in files:
        content = f.read_text(encoding="utf-8")
        fm, _body = parse_skill_frontmatter(content)
        has_fm = bool(fm)

        if has_fm:
            skills_with_frontmatter += 1
        else:
            skills_without_frontmatter += 1

        file_stem = f.stem
        pname = parent_dir_name(f)
        fm_name = fm.get("name", "")
        fm_category = fm.get("category", "")
        triggers = fm.get("triggers", []) if isinstance(fm.get("triggers"), list) else []
        dependencies = fm.get("dependencies", []) if isinstance(fm.get("dependencies"), list) else []
        related = fm.get("related", []) if isinstance(fm.get("related"), list) else []
        priority = fm.get("priority", "")
        estimated_tokens = fm.get("estimated_tokens", "")

        # --- name mismatch ---
        if has_fm and fm_name and fm_name != file_stem:
            name_mismatches.append({
                "skill": str(f.relative_to(SKILLS_ROOT)),
                "frontmatter_name": fm_name,
                "file_stem": file_stem,
            })

        # --- category mismatch ---
        if has_fm and fm_category:
            # Root-level files have parent_dir == "skills" which isn't in CATEGORIES
            # They are implicitly "core". Subdir files should match their parent dir.
            expected_category = pname if pname in CATEGORIES else None
            if expected_category and fm_category != expected_category:
                category_mismatches.append({
                    "skill": str(f.relative_to(SKILLS_ROOT)),
                    "frontmatter_category": fm_category,
                    "parent_dir": pname,
                })

        # --- invalid references ---
        for ref in dependencies:
            if not resolve_ref_path(f, ref, SKILLS_ROOT):
                invalid_references.append({
                    "skill": str(f.relative_to(SKILLS_ROOT)),
                    "field": "dependencies",
                    "reference": ref,
                })
        for ref in related:
            if not resolve_ref_path(f, ref, SKILLS_ROOT):
                invalid_references.append({
                    "skill": str(f.relative_to(SKILLS_ROOT)),
                    "field": "related",
                    "reference": ref,
                })

        # --- missing fields ---
        expected = ["name", "category", "triggers", "dependencies", "related", "priority"]
        missing = [k for k in expected if k not in fm]
        if missing:
            missing_fields.append({
                "skill": str(f.relative_to(SKILLS_ROOT)),
                "missing_fields": missing,
            })

        # --- trigger collection for duplicate detection ---
        for t in triggers:
            trigger_map.setdefault(t, []).append(str(f.relative_to(SKILLS_ROOT)))

        all_skills.append({
            "name": fm_name or file_stem,
            "category": fm_category or pname,
            "has_frontmatter": has_fm,
            "triggers_count": len(triggers),
            "dependencies_count": len(dependencies),
            "related_count": len(related),
            "priority": priority,
            "estimated_tokens": estimated_tokens,
        })

    # Duplicate triggers
    duplicate_triggers = [
        {"trigger": t, "skills": skills}
        for t, skills in sorted(trigger_map.items())
        if len(skills) > 1
    ]

    return {
        "total_skills": len(files),
        "skills_with_frontmatter": skills_with_frontmatter,
        "skills_without_frontmatter": skills_without_frontmatter,
        "invalid_references": invalid_references,
        "name_mismatches": name_mismatches,
        "category_mismatches": category_mismatches,
        "missing_fields": missing_fields,
        "duplicate_triggers": duplicate_triggers,
        "all_skills": all_skills,
    }


def main():
    report = audit()
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
