"""Tests for environment detector."""
import pytest
from python_skills.detector import detect_environment
from python_skills.config import Target


@pytest.fixture
def temp_project(tmp_path):
    return tmp_path


class TestEnvironmentDetector:
    def test_detect_all_returns_all_targets(self, temp_project):
        summary = detect_environment(temp_project)
        assert len(summary.targets) == len(Target)

    def test_all_targets_have_results(self, temp_project):
        summary = detect_environment(temp_project)
        for target in Target:
            assert target.value in summary.targets

    def test_universal_always_detected(self, temp_project):
        summary = detect_environment(temp_project)
        assert summary.targets["universal"].adapter_available is True

    def test_aider_detected_when_config_exists(self, temp_project):
        (temp_project / ".aider.conf.yml").touch()
        summary = detect_environment(temp_project)
        assert summary.targets["aider"].project_config_detected is True

    def test_gemini_detected_when_gemini_md_exists(self, temp_project):
        (temp_project / "GEMINI.md").touch()
        summary = detect_environment(temp_project)
        assert summary.targets["gemini"].project_config_detected is True

    def test_codex_detected_when_agents_md_exists(self, temp_project):
        (temp_project / "AGENTS.md").touch()
        summary = detect_environment(temp_project)
        assert summary.targets["codex"].project_config_detected is True

    def test_roo_detected_when_roo_dir_exists(self, temp_project):
        (temp_project / ".roo").mkdir()
        summary = detect_environment(temp_project)
        assert summary.targets["roo"].project_config_detected is True
