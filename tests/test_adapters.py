"""Tests for AgentSkillsAdapter and target adapters."""
import pytest
from pathlib import Path
import tempfile
import shutil
from python_skills.config import Target, Scope, get_adapter_capabilities, AdapterCapabilities
from python_skills.skills.registry import get_registry
from python_skills.state import LockManager
from python_skills.adapters import get_adapter
from python_skills.adapters.agent_skills import AgentSkillsAdapter, _skill_name_to_slug, _generate_skill_md
from python_skills.skills.metadata import SkillMetadata


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory."""
    (tmp_path / "src").mkdir()
    return tmp_path


@pytest.fixture
def registry():
    return get_registry()


@pytest.fixture
def lock_manager(temp_project):
    return LockManager(temp_project)


class TestAgentSkillsAdapterHelpers:
    def test_skill_name_to_slug(self):
        assert _skill_name_to_slug("async_concurrency") == "async-concurrency"
        assert _skill_name_to_slug("SQLInjectionPrevention") == "sqlinjectionprevention"

    def test_generate_skill_md(self):
        skill = SkillMetadata(
            name="test-skill", category="testing", path=Path("test.md"),
            description="A test skill"
        )
        content = "# Testing\n\nThis is a test skill."
        md = _generate_skill_md(skill, content)
        assert "---" in md
        assert "name: test-skill" in md
        assert "description: A test skill" in md
        assert "# Testing" in md


class TestOpenCodeAdapter:
    def test_detect(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.OPENCODE, temp_project, registry, lock_manager, None)
        result = adapter.detect()
        assert result.adapter_available is True

    def test_install_dry_run(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.OPENCODE, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=True)
        assert result.success is True
        assert len(result.errors) == 0

    def test_status_not_installed(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.OPENCODE, temp_project, registry, lock_manager, None)
        result = adapter.status(scope="project")
        assert result.installed is False


class TestWindsurfAdapter:
    def test_install_creates_files(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.WINDSURF, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=False)
        assert result.success is True
        assert len(result.files_created) > 0


class TestVSCodeAdapter:
    def test_install(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.VSCODE, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=True)
        assert result.success is True


class TestGeminiAdapter:
    def test_install(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.GEMINI, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=True)
        assert result.success is True


class TestCodexAdapter:
    def test_install(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.CODEX, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=True)
        assert result.success is True


class TestRooAdapter:
    def test_install(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.ROO, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=True)
        assert result.success is True


class TestGooseAdapter:
    def test_install(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.GOOSE, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=True)
        assert result.success is True


class TestJunieAdapter:
    def test_install(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.JETBRAINS, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=True)
        assert result.success is True


class TestZedAdapter:
    def test_install(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.ZED, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=True)
        assert result.success is True


class TestContinueAdapter:
    def test_install(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.CONTINUE, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=True)
        assert result.success is True


class TestAiderAdapter:
    def test_install(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.AIDER, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=True)
        assert result.success is True


class TestClineAdapter:
    def test_install(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.CLINE, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=True)
        assert result.success is True


class TestUniversalAdapter:
    def test_install(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.UNIVERSAL, temp_project, registry, lock_manager, None)
        result = adapter.install(scope="project", dry_run=True)
        assert result.success is True


class TestAllAdaptersInstantiate:
    def test_all_targets_have_adapter(self, temp_project, registry, lock_manager):
        for target in Target:
            adapter = get_adapter(target, temp_project, registry, lock_manager, None)
            assert adapter is not None
            assert hasattr(adapter, 'install')
            assert hasattr(adapter, 'uninstall')
            assert hasattr(adapter, 'sync')
            assert hasattr(adapter, 'status')
