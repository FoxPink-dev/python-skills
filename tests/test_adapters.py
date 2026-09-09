"""Tests for AgentSkillsAdapter and target adapters."""
import pytest
from pathlib import Path
from python_skills.config import Target
from python_skills.skills.registry import get_registry
from python_skills.state import LockManager
from python_skills.adapters import get_adapter
from python_skills.adapters.agent_skills import _skill_name_to_slug, _generate_skill_md
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


class TestOwnershipMarkers:
    """Verify SKILL.md files get ownership markers for status/uninstall."""

    def test_install_adds_markers(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.OPENCODE, temp_project, registry, lock_manager, None)
        adapter.install(scope="project", dry_run=False)
        sample = temp_project / ".agents" / "skills" / "async-concurrency" / "SKILL.md"
        content = sample.read_text(encoding="utf-8")
        assert "<!-- BEGIN PYTHON-SKILLS MANAGED -->" in content
        assert "<!-- END PYTHON-SKILLS MANAGED -->" in content

    def test_status_detects_managed_files(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.OPENCODE, temp_project, registry, lock_manager, None)
        adapter.install(scope="project", dry_run=False)
        status = adapter.status(scope="project")
        assert status.installed is True
        assert len(status.files) > 0

    def test_uninstall_removes_managed_files(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.OPENCODE, temp_project, registry, lock_manager, None)
        adapter.install(scope="project", dry_run=False)
        result = adapter.uninstall(scope="project", dry_run=False)
        assert len(result.files_removed) > 0
        status = adapter.status(scope="project")
        assert status.installed is False


class TestSyncBehavior:
    """Verify sync correctly detects changes and skips unchanged."""

    def test_sync_no_changes(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.OPENCODE, temp_project, registry, lock_manager, None)
        adapter.install(scope="project", dry_run=False)
        result = adapter.sync(scope="project", dry_run=False)
        assert len(result.added) == 0
        assert len(result.modified) == 0
        assert len(result.removed) == 0
        assert len(result.skipped) > 0

    def test_sync_idempotent(self, temp_project, registry, lock_manager):
        adapter = get_adapter(Target.OPENCODE, temp_project, registry, lock_manager, None)
        adapter.install(scope="project", dry_run=False)
        adapter.sync(scope="project", dry_run=False)
        adapter.sync(scope="project", dry_run=False)
        status = adapter.status(scope="project")
        assert status.installed is True


class TestSharedAgentSkills:
    """Verify .agents/skills/ shared resource deduplication and safety."""

    def test_shared_dir_not_duplicated(self, temp_project, registry, lock_manager):
        for t in [Target.OPENCODE, Target.WINDSURF, Target.GEMINI]:
            a = get_adapter(t, temp_project, registry, lock_manager, None)
            a.install(scope="project", dry_run=False)
        agents = temp_project / ".agents" / "skills"
        assert agents.exists()
        count = sum(1 for _ in agents.iterdir() if _.is_dir())
        assert count == 67

    def test_native_dirs_separate(self, temp_project, registry, lock_manager):
        for t in [Target.OPENCODE, Target.WINDSURF, Target.GEMINI]:
            a = get_adapter(t, temp_project, registry, lock_manager, None)
            a.install(scope="project", dry_run=False)
        for d in [".opencode/skills", ".windsurf/skills", ".gemini/skills"]:
            p = temp_project / d
            assert p.exists()
            count = sum(1 for _ in p.iterdir() if _.is_dir())
            assert count == 67

    def test_uninstall_preserves_shared_for_other_consumers(self, temp_project, registry, lock_manager):
        for t in [Target.OPENCODE, Target.WINDSURF, Target.GEMINI]:
            a = get_adapter(t, temp_project, registry, lock_manager, None)
            a.install(scope="project", dry_run=False)
        # Uninstall OpenCode
        a1 = get_adapter(Target.OPENCODE, temp_project, registry, lock_manager, None)
        a1.uninstall(scope="project", dry_run=False)
        # Shared dir should remain
        agents = temp_project / ".agents" / "skills"
        assert agents.exists()
        count = sum(1 for _ in agents.iterdir() if _.is_dir())
        assert count == 67
        # Native dir should be cleaned
        assert not (temp_project / ".opencode" / "skills").exists() or \
               sum(1 for _ in (temp_project / ".opencode" / "skills").iterdir()) == 0

    def test_uninstall_removes_native_dir(self, temp_project, registry, lock_manager):
        a = get_adapter(Target.OPENCODE, temp_project, registry, lock_manager, None)
        a.install(scope="project", dry_run=False)
        a.uninstall(scope="project", dry_run=False)
        native = temp_project / ".opencode" / "skills"
        if native.exists():
            assert sum(1 for _ in native.iterdir()) == 0


class TestAdaptersHaveCorrectPaths:
    """Verify each AgentSkillsAdapter has correct path configuration."""

    @pytest.mark.parametrize("target,agent_dir,native_dir", [
        (Target.OPENCODE, ".agents/skills", ".opencode/skills"),
        (Target.WINDSURF, ".agents/skills", ".windsurf/skills"),
        (Target.VSCODE, ".agents/skills", ".github/skills"),
        (Target.GEMINI, ".agents/skills", ".gemini/skills"),
        (Target.ROO, ".agents/skills", ".roo/skills"),
        (Target.CODEX, ".agents/skills", None),
        (Target.GOOSE, ".agents/skills", None),
        (Target.JETBRAINS, ".agents/skills", ".junie/skills"),
        (Target.ZED, ".agents/skills", None),
    ])
    def test_agent_skills_dirs(self, target, agent_dir, native_dir, temp_project, registry, lock_manager):
        adapter = get_adapter(target, temp_project, registry, lock_manager, None)
        assert adapter.agent_skills_dir == agent_dir
        assert adapter.native_skills_dir == native_dir
