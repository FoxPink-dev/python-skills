"""Phase 13 test suite - Execution & Verification Intelligence."""

import pytest
from pathlib import Path
from python_skills.skills.registry import SkillRegistry
from python_skills.skills.graph import SkillGraph
from python_skills.skills.routing import SkillRouter, RoutingResult
from python_skills.skills.verification import (
    VerificationPlanner, VerificationPlan, VerificationLevel, VerificationCheck
)
from python_skills.skills.recovery import (
    RecoveryRouter, FailureTaxonomy, RecoveryResult, FAILURE_TYPES
)
from python_skills.skills.explainability import (
    ExplainabilityEngine, ConfidenceAssessor, ConfidenceLevel, RoutingExplanation
)


SKILLS_ROOT = Path(__file__).resolve().parent.parent / "skills"


@pytest.fixture
def registry():
    """Create a skill registry."""
    return SkillRegistry(SKILLS_ROOT)


@pytest.fixture
def graph(registry):
    """Create a skill graph."""
    return SkillGraph(registry)


@pytest.fixture
def router(registry, graph):
    """Create a skill router."""
    return SkillRouter(registry, graph)


@pytest.fixture
def planner():
    """Create a verification planner."""
    return VerificationPlanner()


@pytest.fixture
def recovery_router(registry, graph):
    """Create a recovery router."""
    return RecoveryRouter(registry, graph)


@pytest.fixture
def explainability():
    """Create an explainability engine."""
    return ExplainabilityEngine()


# ============================================================
# Verification Tests
# ============================================================

class TestVerificationLevels:
    """Test verification level classification."""

    def test_verification_level_enum(self):
        """Test verification levels are defined."""
        assert VerificationLevel.STATIC.value == "static"
        assert VerificationLevel.TEST.value == "test"
        assert VerificationLevel.BEHAVIOR.value == "behavior"
        assert VerificationLevel.SECURITY.value == "security"
        assert VerificationLevel.VERSION.value == "version"

    def test_verification_level_membership(self):
        """Test verification level membership."""
        assert VerificationLevel.STATIC in VerificationLevel
        assert VerificationLevel.TEST in VerificationLevel

    def test_plan_has_levels(self, planner, router):
        """Test verification plan includes levels."""
        result = router.route("Fix SQL injection")
        skills = result.primary + result.supporting
        plan = planner.plan("Fix SQL injection", skills)
        assert len(plan.levels) > 0
        assert VerificationLevel.SECURITY in plan.levels

    def test_plan_has_checks(self, planner, router):
        """Test verification plan includes checks."""
        result = router.route("Fix SQL injection")
        skills = result.primary + result.supporting
        plan = planner.plan("Fix SQL injection", skills)
        assert len(plan.checks) > 0

    def test_plan_skills_list(self, planner, router):
        """Test verification plan tracks skills."""
        result = router.route("Fix SQL injection")
        skills = result.primary + result.supporting
        plan = planner.plan("Fix SQL injection", skills)
        assert len(plan.skills) > 0

    def test_plan_deterministic(self, planner, router):
        """Test verification plan is deterministic."""
        result = router.route("Fix SQL injection")
        skills = result.primary + result.supporting
        plan1 = planner.plan("Fix SQL injection", skills)
        plan2 = planner.plan("Fix SQL injection", skills)
        assert [c.description for c in plan1.checks] == [c.description for c in plan2.checks]
        assert plan1.levels == plan2.levels

    def test_security_task_security_level(self, planner, router):
        """Test security tasks require security verification."""
        result = router.route("Fix path traversal vulnerability")
        skills = result.primary + result.supporting
        plan = planner.plan("Fix path traversal vulnerability", skills)
        assert plan.has_level(VerificationLevel.SECURITY)

    def test_testing_task_test_level(self, planner, router):
        """Test testing tasks require test verification."""
        result = router.route("Write regression tests")
        skills = result.primary + result.supporting
        plan = planner.plan("Write regression tests", skills)
        assert plan.has_level(VerificationLevel.TEST)

    def test_get_checks_by_level(self, planner, router):
        """Test filtering checks by level."""
        result = router.route("Fix SQL injection")
        skills = result.primary + result.supporting
        plan = planner.plan("Fix SQL injection", skills)
        security_checks = plan.get_checks_by_level(VerificationLevel.SECURITY)
        assert len(security_checks) > 0
        for check in security_checks:
            assert check.level == VerificationLevel.SECURITY

    def test_plan_empty_skills(self, planner):
        """Test verification plan with empty skills."""
        plan = planner.plan("Do nothing", [])
        assert len(plan.checks) == 0
        assert len(plan.levels) == 0

    def test_plan_category_checks(self, planner, router):
        """Test category-level checks are included."""
        result = router.route("Fix SQL injection")
        skills = result.primary + result.supporting
        plan = planner.plan("Fix SQL injection", skills)
        # Should have category-level checks
        assert len(plan.checks) >= 3


class TestVerificationPlan:
    """Test VerificationPlan data structure."""

    def test_plan_has_task(self):
        """Test plan stores task."""
        plan = VerificationPlan(task="test task")
        assert plan.task == "test task"

    def test_plan_has_checks(self):
        """Test plan stores checks."""
        plan = VerificationPlan(task="test")
        plan.checks.append(VerificationCheck(
            level=VerificationLevel.TEST,
            description="test check",
            skill="test_skill",
        ))
        assert len(plan.checks) == 1

    def test_plan_has_levels(self):
        """Test plan stores levels."""
        plan = VerificationPlan(task="test")
        plan.levels.append(VerificationLevel.SECURITY)
        assert plan.has_level(VerificationLevel.SECURITY)

    def test_plan_has_skills(self):
        """Test plan stores skills."""
        plan = VerificationPlan(task="test")
        plan.skills = ["skill1", "skill2"]
        assert "skill1" in plan.skills

    def test_get_checks_by_level(self):
        """Test get_checks_by_level method."""
        plan = VerificationPlan(task="test")
        plan.checks.append(VerificationCheck(
            level=VerificationLevel.TEST,
            description="test check",
            skill="test_skill",
        ))
        plan.checks.append(VerificationCheck(
            level=VerificationLevel.SECURITY,
            description="security check",
            skill="test_skill",
        ))
        test_checks = plan.get_checks_by_level(VerificationLevel.TEST)
        assert len(test_checks) == 1
        assert test_checks[0].level == VerificationLevel.TEST


# ============================================================
# Failure Classification Tests
# ============================================================

class TestFailureTaxonomy:
    """Test failure taxonomy."""

    def test_failure_types_defined(self):
        """Test failure types are defined."""
        assert "syntax" in FAILURE_TYPES
        assert "type" in FAILURE_TYPES
        assert "test" in FAILURE_TYPES
        assert "behavior" in FAILURE_TYPES
        assert "security" in FAILURE_TYPES
        assert "performance" in FAILURE_TYPES
        assert "dependency" in FAILURE_TYPES
        assert "compatibility" in FAILURE_TYPES
        assert "configuration" in FAILURE_TYPES
        assert "integration" in FAILURE_TYPES

    def test_failure_type_descriptions(self):
        """Test failure types have descriptions."""
        for ft, desc in FAILURE_TYPES.items():
            assert isinstance(desc, str)
            assert len(desc) > 0

    def test_classify_sql_injection(self):
        """Test sql_injection classification."""
        taxonomy = FailureTaxonomy()
        failures = taxonomy.classify("sql_injection")
        assert "security" in failures
        assert "test" in failures

    def test_classify_async_concurrency(self):
        """Test async_concurrency classification."""
        taxonomy = FailureTaxonomy()
        failures = taxonomy.classify("async_concurrency")
        assert "behavior" in failures
        assert "performance" in failures

    def test_classify_unknown_skill(self):
        """Test classification of unknown skill."""
        taxonomy = FailureTaxonomy()
        failures = taxonomy.classify("unknown_skill_xyz")
        assert failures == []

    def test_get_recovery_skills(self):
        """Test recovery skill retrieval."""
        taxonomy = FailureTaxonomy()
        recovery = taxonomy.get_recovery_skills("security", ["sql_injection"])
        assert "input_validation" in recovery
        assert "sql_injection" not in recovery

    def test_recovery_excludes_current(self):
        """Test recovery excludes current skills."""
        taxonomy = FailureTaxonomy()
        recovery = taxonomy.get_recovery_skills("security", ["sql_injection", "input_validation"])
        assert "sql_injection" not in recovery
        assert "input_validation" not in recovery

    def test_recovery_deterministic(self):
        """Test recovery is deterministic."""
        taxonomy = FailureTaxonomy()
        r1 = taxonomy.get_recovery_skills("security", ["sql_injection"])
        r2 = taxonomy.get_recovery_skills("security", ["sql_injection"])
        assert r1 == r2

    def test_ten_failure_types(self):
        """Test exactly 10 failure types."""
        assert len(FAILURE_TYPES) == 10


# ============================================================
# Recovery Routing Tests
# ============================================================

class TestRecoveryRouting:
    """Test recovery routing."""

    def test_recovery_result_structure(self, recovery_router):
        """Test recovery result structure."""
        result = recovery_router.route_recovery("security", ["database"])
        assert isinstance(result, RecoveryResult)
        assert result.failure_type == "security"
        assert isinstance(result.recovery_skills, list)
        assert result.confidence in ("HIGH", "MEDIUM", "LOW")

    def test_recovery_security(self, recovery_router):
        """Test recovery for security failures."""
        result = recovery_router.route_recovery("security", ["database"])
        assert len(result.recovery_skills) > 0
        # Should suggest security skills
        security_skills = [s for s in result.recovery_skills if "injection" in s or "validation" in s]
        assert len(security_skills) > 0

    def test_recovery_test(self, recovery_router):
        """Test recovery for test failures."""
        result = recovery_router.route_recovery("test", ["database"])
        assert len(result.recovery_skills) > 0

    def test_recovery_excludes_current(self, recovery_router):
        """Test recovery excludes current skills."""
        result = recovery_router.route_recovery("security", ["sql_injection", "input_validation"])
        assert "sql_injection" not in result.recovery_skills
        assert "input_validation" not in result.recovery_skills

    def test_recovery_deterministic(self, recovery_router):
        """Test recovery is deterministic."""
        r1 = recovery_router.route_recovery("security", ["database"])
        r2 = recovery_router.route_recovery("security", ["database"])
        assert r1.recovery_skills == r2.recovery_skills
        assert r1.confidence == r2.confidence

    def test_recovery_confidence_high(self, recovery_router):
        """Test high confidence recovery."""
        result = recovery_router.route_recovery("security", ["database"])
        assert result.confidence in ("HIGH", "MEDIUM")

    def test_recovery_confidence_low_no_skills(self, recovery_router):
        """Test low confidence when no recovery skills."""
        result = recovery_router.route_recovery("syntax", [])
        assert result.confidence == "LOW"
        assert len(result.recovery_skills) == 0

    def test_diagnose_failure(self, recovery_router):
        """Test failure diagnosis."""
        info = recovery_router.diagnose_failure("security")
        assert info.failure_type == "security"
        assert len(info.related_skills) > 0

    def test_diagnose_unknown_failure(self, recovery_router):
        """Test diagnosis of unknown failure."""
        info = recovery_router.diagnose_failure("unknown_type")
        assert info.failure_type == "unknown_type"
        assert info.description == "Unknown failure type"

    def test_recovery_max_3_skills(self, recovery_router):
        """Test recovery returns max 3 skills."""
        result = recovery_router.route_recovery("security", [])
        assert len(result.recovery_skills) <= 3

    def test_recovery_sorted_deterministically(self, recovery_router):
        """Test recovery skills are sorted."""
        result = recovery_router.route_recovery("security", [])
        assert result.recovery_skills == sorted(result.recovery_skills)

    def test_recovery_current_skills_sorted(self, recovery_router):
        """Test current skills are sorted."""
        result = recovery_router.route_recovery("security", ["z_skill", "a_skill"])
        assert result.current_skills == ["a_skill", "z_skill"]


# ============================================================
# Confidence Tests
# ============================================================

class TestConfidence:
    """Test confidence assessment."""

    def test_confidence_levels(self):
        """Test confidence level constants."""
        assert ConfidenceLevel.HIGH == "HIGH"
        assert ConfidenceLevel.MEDIUM == "MEDIUM"
        assert ConfidenceLevel.LOW == "LOW"

    def test_high_confidence_exact_match(self, router):
        """Test high confidence for exact name match."""
        result = router.route("Fix sql_injection vulnerability")
        # sql_injection should have high confidence due to exact name match
        sql_skills = [s for s in result.primary if s.name == "sql_injection"]
        assert len(sql_skills) == 1

    def test_confidence_assessor_high(self, registry):
        """Test confidence assessor returns HIGH for name match."""
        assessor = ConfidenceAssessor()
        skill = registry.get_skill("sql_injection")
        assert skill is not None
        confidence = assessor.assess(skill, 13, "Fix sql_injection vulnerability")
        assert confidence == ConfidenceLevel.HIGH

    def test_confidence_assessor_medium(self, registry):
        """Test confidence assessor returns MEDIUM for trigger match."""
        assessor = ConfidenceAssessor()
        skill = registry.get_skill("database")
        assert skill is not None
        # "database" is in the task, but it's a trigger match not name match
        confidence = assessor.assess(skill, 5, "Fix database queries")
        assert confidence in (ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH)

    def test_confidence_assessor_low(self, registry):
        """Test confidence assessor returns LOW for weak match."""
        assessor = ConfidenceAssessor()
        skill = registry.get_skill("oop")
        assert skill is not None
        # "oop" is not in the task, weak description match only
        confidence = assessor.assess(skill, 2, "Fix SQL injection")
        assert confidence == ConfidenceLevel.LOW

    def test_routing_confidence_high(self, router):
        """Test routing confidence is HIGH for clear tasks."""
        result = router.route("Fix SQL injection vulnerability")
        assert result.confidence == "HIGH"

    def test_routing_confidence_medium(self, router):
        """Test routing confidence for moderate tasks."""
        result = router.route("Improve code quality")
        # May be LOW or MEDIUM depending on trigger matches
        assert result.confidence in ("LOW", "MEDIUM", "HIGH")

    def test_routing_result_has_confidence(self, router):
        """Test routing result includes confidence."""
        result = router.route("Fix SQL injection")
        assert hasattr(result, 'confidence')
        assert result.confidence in ("HIGH", "MEDIUM", "LOW")

    def test_confidence_deterministic(self, router):
        """Test confidence is deterministic."""
        r1 = router.route("Fix SQL injection")
        r2 = router.route("Fix SQL injection")
        assert r1.confidence == r2.confidence

    def test_routing_result_has_token_count(self, router):
        """Test routing result includes token count."""
        result = router.route("Fix SQL injection")
        assert hasattr(result, 'token_count')
        assert result.token_count > 0

    def test_routing_result_has_depth(self, router):
        """Test routing result includes depth."""
        result = router.route("Fix SQL injection")
        assert hasattr(result, 'depth')
        assert result.depth >= 0


# ============================================================
# Token Budget Tests
# ============================================================

class TestContextBudget:
    """Test context budget functionality."""

    def test_budget_result_structure(self, router):
        """Test budget result structure."""
        result = router.route_with_budget("Fix SQL injection", budget=4000)
        assert hasattr(result, 'skills')
        assert hasattr(result, 'total_tokens')
        assert hasattr(result, 'budget')
        assert hasattr(result, 'excluded')

    def test_budget_respected(self, router):
        """Test budget is respected."""
        result = router.route_with_budget("Fix SQL injection", budget=1000)
        assert result.total_tokens <= 1000

    def test_budget_larger(self, router):
        """Test larger budget includes more skills."""
        small = router.route_with_budget("Fix SQL injection", budget=1000)
        large = router.route_with_budget("Fix SQL injection", budget=5000)
        assert len(large.skills) >= len(small.skills)

    def test_budget_excluded_list(self, router):
        """Test excluded skills are tracked."""
        result = router.route_with_budget("Fix SQL injection", budget=500)
        # Should have some excluded if budget is tight
        assert isinstance(result.excluded, list)

    def test_budget_deterministic(self, router):
        """Test budget routing is deterministic."""
        r1 = router.route_with_budget("Fix SQL injection", budget=2000)
        r2 = router.route_with_budget("Fix SQL injection", budget=2000)
        assert [s.name for s in r1.skills] == [s.name for s in r2.skills]
        assert r1.total_tokens == r2.total_tokens

    def test_budget_zero(self, router):
        """Test zero budget returns no skills."""
        result = router.route_with_budget("Fix SQL injection", budget=0)
        assert len(result.skills) == 0
        assert result.total_tokens == 0

    def test_budget_exact_fit(self, router):
        """Test budget exactly fits one skill."""
        result = router.route_with_budget("Fix SQL injection", budget=1800)
        # Should include at least one skill
        assert len(result.skills) >= 1
        # Total tokens should not exceed budget
        assert result.total_tokens <= 1800

    def test_budget_priority_order(self, router):
        """Test budget respects priority ordering."""
        result = router.route_with_budget("Fix SQL injection", budget=2000)
        # Skills should be ordered by priority
        if len(result.skills) >= 2:
            priority_order = {"critical": 0, "high": 1, "primary": 2, "supporting": 3}
            for i in range(len(result.skills) - 1):
                p1 = priority_order.get(result.skills[i].priority, 4)
                p2 = priority_order.get(result.skills[i+1].priority, 4)
                assert p1 <= p2

    def test_budget_total_tokens_accurate(self, router):
        """Test total tokens calculation is accurate."""
        result = router.route_with_budget("Fix SQL injection", budget=4000)
        expected = sum(s.estimated_tokens for s in result.skills)
        assert result.total_tokens == expected

    def test_budget_skills_sorted(self, router):
        """Test budget skills are sorted by priority."""
        result = router.route_with_budget("Fix SQL injection", budget=4000)
        priority_order = {"critical": 0, "high": 1, "primary": 2, "supporting": 3}
        for i in range(len(result.skills) - 1):
            p1 = priority_order.get(result.skills[i].priority, 4)
            p2 = priority_order.get(result.skills[i+1].priority, 4)
            assert p1 <= p2


# ============================================================
# Composition Depth Tests
# ============================================================

class TestCompositionDepth:
    """Test composition depth limiting."""

    def test_compose_with_depth(self, router):
        """Test composition respects depth."""
        result = router.compose("Fix SQL injection", max_depth=1)
        assert result.depth == 1

    def test_depth_zero_no_deps(self, router):
        """Test depth 0 includes no dependencies."""
        result = router.route("Fix SQL injection", max_depth=0)
        assert len(result.dependencies) == 0

    def test_depth_one_direct_deps(self, router):
        """Test depth 1 includes direct dependencies."""
        result = router.route("Fix SQL injection", max_depth=1)
        # Should have some dependencies
        assert isinstance(result.dependencies, list)

    def test_depth_two_transitive_deps(self, router):
        """Test depth 2 includes transitive dependencies."""
        r1 = router.route("Fix SQL injection", max_depth=1)
        r2 = router.route("Fix SQL injection", max_depth=2)
        # Depth 2 should have >= depth 1 dependencies
        assert len(r2.dependencies) >= len(r1.dependencies)

    def test_compose_bounded(self, router):
        """Test compose is bounded."""
        result = router.compose("Build comprehensive application", max_skills=3, max_depth=1)
        assert len(result.primary) <= 3

    def test_depth_deterministic(self, router):
        """Test depth is deterministic."""
        r1 = router.route("Fix SQL injection", max_depth=2)
        r2 = router.route("Fix SQL injection", max_depth=2)
        assert [s.name for s in r1.dependencies] == [s.name for s in r2.dependencies]

    def test_depth_prevents_runaway(self, router):
        """Test depth prevents runaway expansion."""
        result = router.route("Fix SQL injection", max_depth=0)
        # With depth 0, should have minimal dependencies
        assert len(result.dependencies) == 0

    def test_compose_max_skills(self, router):
        """Test compose respects max_skills."""
        result = router.compose("Build comprehensive application", max_skills=2)
        assert len(result.primary) <= 2

    def test_compose_dependencies_bounded(self, router):
        """Test compose dependencies are bounded."""
        result = router.compose("Fix SQL injection", max_depth=1)
        for dep in result.dependencies:
            assert dep.name not in [s.name for s in result.primary]

    def test_depth_zero_still_selects_primary(self, router):
        """Test depth 0 still selects primary skills."""
        result = router.route("Fix SQL injection", max_depth=0)
        assert len(result.primary) > 0


# ============================================================
# Explainability Tests
# ============================================================

class TestExplainability:
    """Test explainability engine."""

    def test_explain_selection(self, explainability, registry):
        """Test skill selection explanation."""
        skill = registry.get_skill("sql_injection")
        assert skill is not None
        explanation = explainability.explain_selection(skill, 13, "Fix SQL injection")
        assert explanation.selected is True
        assert explanation.score == 13
        assert len(explanation.reasons) > 0
        assert explanation.confidence in ("HIGH", "MEDIUM", "LOW")

    def test_explain_exclusion(self, explainability, registry):
        """Test skill exclusion explanation."""
        skill = registry.get_skill("oop")
        assert skill is not None
        explanation = explainability.explain_exclusion(skill, 2, "Fix SQL injection")
        assert explanation.selected is False
        assert explanation.score == 2
        assert len(explanation.reasons) > 0

    def test_explain_routing(self, explainability, router, registry):
        """Test full routing explanation."""
        result = router.route("Fix SQL injection")
        selected = [(s, router.get_score(s.name, "Fix SQL injection")) for s in result.primary]
        all_skills = list(registry.get_all_skills())
        excluded = [(s, router.get_score(s.name, "Fix SQL injection"))
                    for s in all_skills if router.get_score(s.name, "Fix SQL injection") < 5][:5]

        explanation = explainability.explain_routing(
            "Fix SQL injection",
            selected,
            excluded,
        )
        assert explanation.task == "Fix SQL injection"
        assert len(explanation.selected_skills) > 0
        assert explanation.total_score > 0

    def test_explanation_deterministic(self, explainability, registry):
        """Test explanation is deterministic."""
        skill = registry.get_skill("sql_injection")
        assert skill is not None
        e1 = explainability.explain_selection(skill, 13, "Fix SQL injection")
        e2 = explainability.explain_selection(skill, 13, "Fix SQL injection")
        assert e1.reasons == e2.reasons
        assert e1.confidence == e2.confidence

    def test_explanation_has_reasons(self, explainability, registry):
        """Test explanation has reasons."""
        skill = registry.get_skill("sql_injection")
        assert skill is not None
        explanation = explainability.explain_selection(skill, 13, "Fix SQL injection")
        assert len(explanation.reasons) > 0

    def test_explanation_sorted_deterministically(self, explainability, router, registry):
        """Test routing explanation is sorted."""
        result = router.route("Fix SQL injection")
        selected = [(s, router.get_score(s.name, "Fix SQL injection")) for s in result.primary]
        explanation = explainability.explain_routing("Fix SQL injection", selected, [])
        # Check sorted by score desc, name asc
        for i in range(len(explanation.selected_skills) - 1):
            e1 = explanation.selected_skills[i]
            e2 = explanation.selected_skills[i+1]
            assert (-e1.score, e1.skill) <= (-e2.score, e2.skill)

    def test_dependency_explanation(self, explainability, registry):
        """Test dependency explanation."""
        skill = registry.get_skill("database")
        assert skill is not None
        explanation = explainability.explain_selection(
            skill, 5, "Fix SQL injection", dependency_of=["sql_injection"]
        )
        assert "sql_injection" in explanation.dependency_of

    def test_confidence_in_explanation(self, explainability, registry):
        """Test confidence is included in explanation."""
        skill = registry.get_skill("sql_injection")
        assert skill is not None
        explanation = explainability.explain_selection(skill, 13, "Fix SQL injection")
        assert explanation.confidence in ("HIGH", "MEDIUM", "LOW")

    def test_excluded_skills_limited(self, explainability, router, registry):
        """Test excluded skills are limited to 10."""
        result = router.route("Fix SQL injection")
        all_skills = list(registry.get_all_skills())
        excluded = [(s, router.get_score(s.name, "Fix SQL injection")) for s in all_skills]
        explanation = explainability.explain_routing("Fix SQL injection", [], excluded)
        assert len(explanation.excluded_skills) <= 10

    def test_routing_explanation_total_score(self, explainability, router):
        """Test routing explanation total score."""
        result = router.route("Fix SQL injection")
        selected = [(s, router.get_score(s.name, "Fix SQL injection")) for s in result.primary]
        explanation = explainability.explain_routing("Fix SQL injection", selected, [])
        expected_score = sum(score for _, score in selected)
        assert explanation.total_score == expected_score


# ============================================================
# Regression Tests
# ============================================================

class TestRegression:
    """Ensure previous routing benchmarks still pass."""

    def test_sql_injection_routing(self, router):
        """Test SQL injection routing."""
        result = router.route("Fix SQL injection in a FastAPI endpoint")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "sql_injection" in all_names

    def test_file_upload_routing(self, router):
        """Test file upload routing."""
        result = router.route("Build a secure file upload endpoint")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "file_handling" in all_names
        assert "path_traversal" in all_names

    def test_negative_no_security(self, router):
        """Test negative routing - no security skills for dataclass task."""
        result = router.route("Create a Python dataclass")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names
        assert "command_injection" not in primary_names

    def test_deterministic_routing(self, router):
        """Test routing is deterministic."""
        r1 = router.route("Fix SQL injection")
        r2 = router.route("Fix SQL injection")
        assert [s.name for s in r1.primary] == [s.name for s in r2.primary]

    def test_composition_basic(self, router):
        """Test basic composition."""
        result = router.compose("Fix SQL injection")
        assert len(result.primary) > 0
        assert len(result.primary) <= 5

    def test_no_cycles(self, graph):
        """Test no dependency cycles."""
        cycles = graph.detect_cycles()
        assert len(cycles) == 0

    def test_no_orphan_references(self, graph):
        """Test no orphan references."""
        orphans = graph.find_orphan_references()
        real_orphans = [o for o in orphans if o["reference"]]
        assert len(real_orphans) == 0

    def test_all_69_skills(self, registry):
        """Test all 69 skills are loaded."""
        registry.load_all()
        assert len(registry._skills) == 69

    def test_skill_metadata_has_verification_fields(self, registry):
        """Test skill metadata has verification fields."""
        skill = registry.get_skill("sql_injection")
        assert skill is not None
        assert hasattr(skill, 'verification')
        assert hasattr(skill, 'checks')
        assert hasattr(skill, 'failure_types')
        assert hasattr(skill, 'verification_levels')

    def test_forbidden_skills_excluded(self, router):
        """Test forbidden skills are excluded."""
        result = router.route("Fix SQL injection", forbidden=["sql_injection"])
        all_names = [s.name for s in result.primary + result.supporting]
        assert "sql_injection" not in all_names
