"""Tests for skill loader and metadata."""
import pytest
from pathlib import Path
from python_skills.skills.loader import SkillLoader
from python_skills.skills.metadata import load_skill_metadata, SkillMetadata


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
