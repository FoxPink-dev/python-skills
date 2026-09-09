"""Tests for config module."""
from python_skills.config import Target, Scope, AdapterCapabilities, get_adapter_capabilities


class TestTarget:
    def test_all_values(self):
        expected = [
            'claude', 'cursor', 'kiro', 'cline', 'opencode', 'windsurf',
            'vscode', 'roo', 'gemini', 'codex', 'jetbrains', 'goose',
            'zed', 'continue', 'aider', 'universal'
        ]
        assert [t.value for t in Target] == expected

    def test_count(self):
        assert len(Target) == 16

    def test_string_enum(self):
        assert isinstance(Target.CLAUDE.value, str)


class TestScope:
    def test_project_and_global(self):
        assert Scope.PROJECT.value == "project"
        assert Scope.GLOBAL.value == "global"


class TestAdapterCapabilities:
    def test_all_targets_have_capabilities(self):
        for target in Target:
            caps = get_adapter_capabilities(target)
            assert isinstance(caps, AdapterCapabilities)

    def test_universal_always_available(self):
        caps = get_adapter_capabilities(Target.UNIVERSAL)
        assert caps.supports_project is True
        assert caps.supports_global is True

    def test_adapter_class_values(self):
        for target in Target:
            caps = get_adapter_capabilities(target)
            assert caps.adapter_class in ("A", "B", "C", "D", "E")

    def test_a_class_has_native_skills(self):
        a_targets = [t for t in Target if get_adapter_capabilities(t).adapter_class == "A"]
        for t in a_targets:
            assert get_adapter_capabilities(t).has_native_skills is True

    def test_b_class_has_native_rules(self):
        b_targets = [t for t in Target if get_adapter_capabilities(t).adapter_class == "B"]
        for t in b_targets:
            assert get_adapter_capabilities(t).has_native_rules is True
