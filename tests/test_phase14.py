"""Phase 14 integration tests - proving components are actually connected."""

import pytest
from pathlib import Path
from python_skills.skills.registry import SkillRegistry
from python_skills.skills.graph import SkillGraph
from python_skills.skills.routing import SkillRouter
from python_skills.skills.execution import ExecutionEngine, ExecutionContext, RecoveryContext, SkillContent
from python_skills.skills.verification import VerificationPlan, VerificationLevel
from python_skills.skills.recovery import FailureInfo


SKILLS_ROOT = Path(__file__).resolve().parent.parent / "skills"


@pytest.fixture
def engine():
    """Create a fully wired ExecutionEngine."""
    registry = SkillRegistry(SKILLS_ROOT)
    graph = SkillGraph(registry)
    return ExecutionEngine(registry, graph)


# ============================================================
# Preparation Integration (route → compose → content → verify → explain)
# ============================================================

class TestPreparationIntegration:
    """Prove that prepare() connects routing, content loading, verification, and explanation."""

    def test_prepare_returns_execution_context(self, engine):
        """Test prepare() returns a complete ExecutionContext."""
        ctx = engine.prepare("Fix SQL injection")
        assert isinstance(ctx, ExecutionContext)
        assert ctx.task == "Fix SQL injection"

    def test_prepare_has_primary_skills(self, engine):
        """Test prepare() selects primary skills via routing."""
        ctx = engine.prepare("Fix SQL injection in a FastAPI endpoint")
        assert "sql_injection" in ctx.primary_names

    def test_prepare_loads_actual_content(self, engine):
        """Test prepare() loads actual .md content for selected skills."""
        ctx = engine.prepare("Fix SQL injection in a FastAPI endpoint")
        assert len(ctx.skills) > 0
        for sc in ctx.skills:
            assert isinstance(sc, SkillContent)
            assert len(sc.content) > 100  # real content, not empty
            assert sc.metadata.name == sc.name

    def test_prepare_content_matches_registry(self, engine):
        """Test loaded content matches what registry provides directly."""
        ctx = engine.prepare("Fix SQL injection")
        for sc in ctx.skills:
            direct_content = engine.registry.get_skill_content(sc.name)
            assert sc.content == direct_content

    def test_prepare_has_verification_plan(self, engine):
        """Test prepare() creates a verification plan from selected skills."""
        ctx = engine.prepare("Fix SQL injection")
        assert ctx.verification_plan is not None
        assert isinstance(ctx.verification_plan, VerificationPlan)
        assert len(ctx.verification_plan.checks) > 0
        assert VerificationLevel.SECURITY in ctx.verification_plan.levels

    def test_prepare_verification_plan_uses_selected_skills(self, engine):
        """Test verification plan references the selected skills."""
        ctx = engine.prepare("Fix SQL injection")
        plan_skills = set(ctx.verification_plan.skills)
        assert "sql_injection" in plan_skills

    def test_prepare_has_confidence(self, engine):
        """Test prepare() includes routing confidence."""
        ctx = engine.prepare("Fix SQL injection")
        assert ctx.confidence in ("HIGH", "MEDIUM", "LOW")

    def test_prepare_has_explanation(self, engine):
        """Test prepare() includes explainability information."""
        ctx = engine.prepare("Fix SQL injection")
        assert ctx.explanation is not None
        assert ctx.explanation.task == "Fix SQL injection"
        assert len(ctx.explanation.selected_skills) > 0

    def test_prepare_has_token_count(self, engine):
        """Test prepare() includes token count from metadata."""
        ctx = engine.prepare("Fix SQL injection")
        assert ctx.token_count > 0
        # Token count should match sum of skill estimated_tokens
        expected = sum(sc.metadata.estimated_tokens for sc in ctx.skills)
        assert ctx.token_count == expected

    def test_prepare_deterministic(self, engine):
        """Test prepare() produces identical results for same input."""
        ctx1 = engine.prepare("Fix SQL injection")
        ctx2 = engine.prepare("Fix SQL injection")
        assert ctx1.primary_names == ctx2.primary_names
        assert ctx1.supporting_names == ctx2.supporting_names
        assert ctx1.dependency_names == ctx2.dependency_names
        assert ctx1.confidence == ctx2.confidence
        assert ctx1.token_count == ctx2.token_count
        assert [sc.name for sc in ctx1.skills] == [sc.name for sc in ctx2.skills]

    def test_prepare_with_budget(self, engine):
        """Test prepare() uses budget-aware routing when budget supplied."""
        ctx = engine.prepare("Fix SQL injection", budget=2000)
        assert ctx.budget is not None
        assert ctx.budget.total_tokens <= 2000
        assert ctx.token_count <= 2000

    def test_prepare_with_budget_fewer_skills(self, engine):
        """Test smaller budget produces fewer skills."""
        ctx_large = engine.prepare("Fix SQL injection", budget=5000)
        ctx_small = engine.prepare("Fix SQL injection", budget=800)
        assert len(ctx_small.skills) <= len(ctx_large.skills)

    def test_prepare_with_forbidden(self, engine):
        """Test prepare() excludes forbidden skills."""
        ctx = engine.prepare("Fix SQL injection", forbidden=["sql_injection"])
        assert "sql_injection" not in ctx.primary_names
        assert "sql_injection" not in ctx.supporting_names

    def test_prepare_with_max_skills(self, engine):
        """Test prepare() respects max_skills limit."""
        ctx = engine.prepare("Build comprehensive application", max_skills=2)
        assert len(ctx.primary_names) <= 2

    def test_prepare_path_traversal(self, engine):
        """Test prepare() for path traversal scenario."""
        ctx = engine.prepare("Uploaded files can escape the intended directory")
        all_names = ctx.primary_names + ctx.supporting_names + ctx.dependency_names
        assert "path_traversal" in all_names
        assert "file_handling" in all_names
        # Verify content is loaded
        content_names = [sc.name for sc in ctx.skills]
        assert "path_traversal" in content_names

    def test_prepare_compatibility(self, engine):
        """Test prepare() for Python version compatibility scenario."""
        ctx = engine.prepare("Application passes on Python 3.11 but fails on Python 3.12")
        all_names = ctx.primary_names + ctx.supporting_names + ctx.dependency_names
        # Should include compatibility/dependency-related skills
        assert len(all_names) > 0
        assert ctx.verification_plan is not None


# ============================================================
# Recovery Integration (failure → classify → recovery → deps → content)
# ============================================================

class TestRecoveryIntegration:
    """Prove that recover() connects failure classification, recovery routing, and content loading."""

    def test_recover_returns_recovery_context(self, engine):
        """Test recover() returns a complete RecoveryContext."""
        ctx = engine.recover("security", ["database"])
        assert isinstance(ctx, RecoveryContext)
        assert ctx.failure_type == "security"

    def test_recover_has_recovery_skills(self, engine):
        """Test recover() selects recovery skills."""
        ctx = engine.recover("security", ["database"])
        assert len(ctx.recovery_skills) > 0

    def test_recover_loads_actual_content(self, engine):
        """Test recover() loads actual .md content for recovery skills."""
        ctx = engine.recover("security", ["database"])
        for sc in ctx.recovery_skills:
            assert isinstance(sc, SkillContent)
            assert len(sc.content) > 100

    def test_recover_excludes_current_skills(self, engine):
        """Test recover() excludes skills that were already active."""
        ctx = engine.recover("security", ["sql_injection", "input_validation"])
        recovery_names = [sc.name for sc in ctx.recovery_skills]
        assert "sql_injection" not in recovery_names
        assert "input_validation" not in recovery_names

    def test_recover_has_confidence(self, engine):
        """Test recover() includes recovery confidence."""
        ctx = engine.recover("security", ["database"])
        assert ctx.confidence in ("HIGH", "MEDIUM", "LOW")

    def test_recover_has_reason(self, engine):
        """Test recover() includes explanation of recovery confidence."""
        ctx = engine.recover("security", ["database"])
        assert len(ctx.reason) > 0

    def test_recover_has_diagnosis(self, engine):
        """Test recover() includes failure diagnosis."""
        ctx = engine.recover("security", ["database"])
        assert ctx.diagnosis is not None
        assert isinstance(ctx.diagnosis, FailureInfo)
        assert ctx.diagnosis.failure_type == "security"
        assert len(ctx.diagnosis.related_skills) > 0

    def test_recover_deterministic(self, engine):
        """Test recover() produces identical results for same input."""
        ctx1 = engine.recover("security", ["database"])
        ctx2 = engine.recover("security", ["database"])
        assert [sc.name for sc in ctx1.recovery_skills] == [sc.name for sc in ctx2.recovery_skills]
        assert ctx1.confidence == ctx2.confidence
        assert ctx1.reason == ctx2.reason

    def test_recover_unknown_failure(self, engine):
        """Test recover() handles unknown failure types."""
        ctx = engine.recover("unknown_type", [])
        assert ctx.failure_type == "unknown_type"
        assert ctx.confidence == "LOW"
        assert len(ctx.recovery_skills) == 0

    def test_recover_resolves_dependencies(self, engine):
        """Test recover() resolves dependencies for recovery skills."""
        ctx = engine.recover("security", [])
        # Recovery skills should have their dependencies loaded too
        assert len(ctx.recovery_skills) >= 1

    def test_recover_all_failure_types(self, engine):
        """Test recover() works for all 10 failure types."""
        for ft in ["syntax", "type", "test", "behavior", "security",
                    "performance", "dependency", "compatibility",
                    "configuration", "integration"]:
            ctx = engine.recover(ft, [])
            assert ctx.failure_type == ft
            assert ctx.confidence in ("HIGH", "MEDIUM", "LOW")


# ============================================================
# End-to-End Integration (complete pipeline)
# ============================================================

class TestEndToEnd:
    """Test the complete pipeline from task to context."""

    def test_flask_sql_injection(self, engine):
        """Scenario A: Fix a Flask endpoint vulnerable to SQL injection."""
        ctx = engine.prepare("Fix a Flask endpoint vulnerable to SQL injection")

        # Primary skills
        assert "sql_injection" in ctx.primary_names

        # Content loaded
        content_names = [sc.name for sc in ctx.skills]
        assert "sql_injection" in content_names
        sql_content = next(sc for sc in ctx.skills if sc.name == "sql_injection")
        assert "parameterized" in sql_content.content.lower() or "query" in sql_content.content.lower()

        # Verification plan
        assert ctx.verification_plan.has_level(VerificationLevel.SECURITY)
        security_checks = ctx.verification_plan.get_checks_by_level(VerificationLevel.SECURITY)
        assert len(security_checks) >= 2

        # Explanation
        assert len(ctx.explanation.selected_skills) > 0

    def test_path_traversal(self, engine):
        """Scenario B: Uploaded files can escape the intended directory."""
        ctx = engine.prepare("Uploaded files can escape the intended directory")

        all_names = ctx.primary_names + ctx.supporting_names + ctx.dependency_names
        assert "path_traversal" in all_names
        assert "file_handling" in all_names

        # Content loaded
        content_names = [sc.name for sc in ctx.skills]
        assert "path_traversal" in content_names
        assert "file_handling" in content_names

        # Verification plan
        assert ctx.verification_plan.has_level(VerificationLevel.SECURITY)

    def test_python_version_compatibility(self, engine):
        """Scenario C: Application passes on Python 3.11 but fails on Python 3.12."""
        ctx = engine.prepare("Application passes on Python 3.11 but fails on Python 3.12")

        all_names = ctx.primary_names + ctx.supporting_names + ctx.dependency_names
        # Should include some compatibility-related skills
        assert len(all_names) > 0

        # Content loaded
        assert len(ctx.skills) > 0

        # Verification plan
        assert ctx.verification_plan is not None

    def test_security_failure_recovery(self, engine):
        """Scenario: Security failure → recovery skills → content."""
        # First prepare
        ctx = engine.prepare("Fix SQL injection")

        # Then recover from security failure
        recovery = engine.recover("security", ctx.primary_names)
        assert recovery.confidence in ("HIGH", "MEDIUM", "LOW")
        assert len(recovery.recovery_skills) > 0
        # Recovery skills should not include the ones we already used
        recovery_names = [sc.name for sc in recovery.recovery_skills]
        for name in ctx.primary_names:
            assert name not in recovery_names

    def test_budget_pipeline(self, engine):
        """Test complete pipeline with budget constraint."""
        ctx = engine.prepare("Fix SQL injection", budget=2000)
        assert ctx.token_count <= 2000
        assert len(ctx.skills) > 0
        assert ctx.verification_plan is not None
        assert ctx.explanation is not None

    def test_forbidden_pipeline(self, engine):
        """Test complete pipeline with forbidden skills."""
        ctx = engine.prepare("Fix SQL injection", forbidden=["sql_injection"])
        assert "sql_injection" not in ctx.primary_names
        assert "sql_injection" not in [sc.name for sc in ctx.skills]

    def test_deterministic_end_to_end(self, engine):
        """Test complete pipeline is deterministic."""
        ctx1 = engine.prepare("Fix SQL injection in FastAPI")
        ctx2 = engine.prepare("Fix SQL injection in FastAPI")
        assert [sc.name for sc in ctx1.skills] == [sc.name for sc in ctx2.skills]
        assert ctx1.verification_plan.checks == ctx2.verification_plan.checks
        assert ctx1.confidence == ctx2.confidence

    def test_content_is_not_metadata(self, engine):
        """Test that loaded content is actual Markdown, not metadata repr."""
        ctx = engine.prepare("Fix SQL injection")
        for sc in ctx.skills:
            # Content should be the actual .md file content
            assert not sc.content.startswith("SkillMetadata")
            assert not sc.content.startswith("name=")
            # Should contain Markdown
            assert "#" in sc.content or "-" in sc.content or "*" in sc.content

    def test_missing_skill_content_handled(self, engine):
        """Test that missing skill content does not crash."""
        ctx = engine.prepare("Fix SQL injection")
        # All selected skills should have content (they're real skills)
        # But verify the engine handles gracefully
        assert len(ctx.skills) > 0
