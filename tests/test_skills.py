"""Tests for skill loader and metadata."""
from pathlib import Path
from python_skills.skills.loader import SkillLoader
from python_skills.skills.metadata import load_skill_metadata
from python_skills.skills.registry import SkillRegistry


SKILLS_ROOT = Path(__file__).resolve().parent.parent / "skills"


class TestSkillLoader:
    def test_load_all_skills(self):
        loader = SkillLoader(SKILLS_ROOT)
        skills = loader.load_all_skills()
        assert len(skills) > 50  # Should have 68 skills

    def test_load_category(self):
        loader = SkillLoader(SKILLS_ROOT)
        stdlib = loader.load_category("stdlib")
        assert len(stdlib) > 0
        assert all(s.category == "stdlib" for s in stdlib)

    def test_get_skill_content(self):
        loader = SkillLoader(SKILLS_ROOT)
        content = loader.get_skill_content("async_concurrency")
        assert content is not None
        assert len(content) > 100

    def test_get_skill_path(self):
        loader = SkillLoader(SKILLS_ROOT)
        path = loader.get_skill_path("async_concurrency")
        assert path is not None
        assert path.exists()

    def test_get_all_skill_names(self):
        loader = SkillLoader(SKILLS_ROOT)
        names = loader.get_all_skill_names()
        assert len(names) > 50
        assert "async_concurrency" in names

    def test_load_nonexistent_skill(self):
        loader = SkillLoader(SKILLS_ROOT)
        assert loader.load_skill("nonexistent_skill_xyz") is None

    def test_root_level_skills_load(self):
        loader = SkillLoader(SKILLS_ROOT)
        # advanced_python.md is at skills/ root
        skill = loader.load_skill("advanced_python")
        assert skill is not None
        assert skill.name == "advanced_python"

    def test_categories_include_core(self):
        loader = SkillLoader(SKILLS_ROOT)
        assert "core" in loader.CATEGORIES


class TestSkillMetadata:
    def test_load_flat_file(self):
        path = SKILLS_ROOT / "stdlib" / "argparse.md"
        meta = load_skill_metadata(path)
        assert meta is not None
        assert meta.name == "argparse"
        assert meta.category == "stdlib"

    def test_get_skill_path_nonexistent(self):
        loader = SkillLoader(SKILLS_ROOT)
        assert loader.get_skill_path("nonexistent") is None

    def test_load_skill_with_related_field(self):
        path = SKILLS_ROOT / "security" / "sql_injection.md"
        meta = load_skill_metadata(path)
        assert meta is not None
        assert meta.name == "sql_injection"
        assert isinstance(meta.related, list)
        assert "engineering/database" in meta.related


class TestSkillRegistry:
    def test_get_related_skills(self):
        registry = SkillRegistry(SKILLS_ROOT)
        related = registry.get_related_skills("sql_injection")
        assert len(related) > 0
        names = [s.name for s in related]
        assert "database" in names

    def test_get_related_skills_nonexistent(self):
        registry = SkillRegistry(SKILLS_ROOT)
        related = registry.get_related_skills("nonexistent_skill_xyz")
        assert related == []

    def test_find_composition(self):
        registry = SkillRegistry(SKILLS_ROOT)
        skills = registry.find_composition("I need to prevent SQL injection")
        assert len(skills) > 0
        names = [s.name for s in skills]
        assert "sql_injection" in names

    def test_find_composition_by_category(self):
        registry = SkillRegistry(SKILLS_ROOT)
        skills = registry.find_composition("security input validation")
        assert len(skills) > 0
        assert any(s.category == "security" for s in skills)

    def test_find_composition_empty_query(self):
        registry = SkillRegistry(SKILLS_ROOT)
        skills = registry.find_composition("")
        assert skills == []
