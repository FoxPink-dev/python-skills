"""Execution context - deterministic integration of routing, verification, and recovery primitives."""

from dataclasses import dataclass, field
from .registry import SkillRegistry
from .graph import SkillGraph
from .routing import SkillRouter, BudgetResult
from .verification import VerificationPlanner, VerificationPlan
from .recovery import RecoveryRouter, FailureInfo
from .explainability import ExplainabilityEngine, RoutingExplanation
from .metadata import SkillMetadata


@dataclass
class SkillContent:
    """A skill with its actual Markdown content loaded."""
    name: str
    metadata: SkillMetadata
    content: str


@dataclass
class ExecutionContext:
    """Deterministic execution context prepared from a task description."""
    task: str
    skills: list[SkillContent] = field(default_factory=list)
    primary_names: list[str] = field(default_factory=list)
    supporting_names: list[str] = field(default_factory=list)
    dependency_names: list[str] = field(default_factory=list)
    verification_plan: VerificationPlan | None = None
    confidence: str = "LOW"
    explanation: RoutingExplanation | None = None
    token_count: int = 0
    budget: BudgetResult | None = None


@dataclass
class RecoveryContext:
    """Deterministic recovery context prepared from a failure report."""
    failure_type: str
    recovery_skills: list[SkillContent] = field(default_factory=list)
    confidence: str = "LOW"
    reason: str = ""
    diagnosis: FailureInfo | None = None


class ExecutionEngine:
    """Thin orchestration layer connecting routing, verification, and recovery primitives.

    This class does NOT execute tasks. It prepares deterministic contexts
    that contain the information an external caller needs to understand
    what skills are relevant, what verification is required, and how to
    recover from failures.

    Determinism guarantee:
        Same task + same skills + same budget → identical ExecutionContext.
    """

    def __init__(self, registry: SkillRegistry, graph: SkillGraph | None = None):
        self.registry = registry
        self.graph = graph or SkillGraph(registry)
        self.graph.build()
        self.router = SkillRouter(registry, self.graph)
        self.verifier = VerificationPlanner()
        self.recovery_router = RecoveryRouter(registry, self.graph)
        self.explainer = ExplainabilityEngine()

    def prepare(
        self,
        task: str,
        budget: int | None = None,
        max_skills: int = 5,
        max_depth: int = 2,
        forbidden: list[str] | None = None,
    ) -> ExecutionContext:
        """Prepare an execution context for a task.

        Flow:
            task → route/compose → load content → verification plan → explanation

        Args:
            task: Task description.
            budget: Optional token budget. When supplied, uses budget-aware routing.
            max_skills: Maximum number of primary skills.
            max_depth: Maximum dependency depth.
            forbidden: Skills to exclude.

        Returns:
            Deterministic ExecutionContext with all information needed by caller.
        """
        # Phase 1: Route
        if budget is not None:
            budget_result = self.router.route_with_budget(task, budget, forbidden, max_depth)
            routing_result = self.router.route(task, forbidden, max_depth)
            # Use budget-filtered skills
            all_skills = budget_result.skills
            primary_names = [s.name for s in all_skills if s in routing_result.primary]
            supporting_names = [s.name for s in all_skills if s in routing_result.supporting]
            dependency_names = [s.name for s in all_skills if s in routing_result.dependencies]
        else:
            routing_result = self.router.route(task, forbidden, max_depth)
            # Apply max_skills limit
            primary = routing_result.primary[:max_skills]
            if len(routing_result.primary) > max_skills:
                supporting = []
            else:
                supporting = routing_result.supporting

            # Recompute dependencies for trimmed primary
            dep_names = set()
            for skill in primary:
                deps = self.router._get_bounded_dependencies(skill.name, max_depth)
                dep_names.update(deps)
            dependencies = []
            seen = {s.name for s in primary}
            for dep_name in sorted(dep_names):
                if dep_name not in seen:
                    dep_skill = self.registry.get_skill(dep_name)
                    if dep_skill:
                        dependencies.append(dep_skill)
                        seen.add(dep_name)

            all_skills = primary + supporting + dependencies
            primary_names = [s.name for s in primary]
            supporting_names = [s.name for s in supporting]
            dependency_names = [s.name for s in dependencies]
            budget_result = None

        # Phase 2: Load content
        skill_contents = self._load_skill_contents(all_skills)

        # Phase 3: Verification plan
        verification_plan = self.verifier.plan(task, all_skills)

        # Phase 4: Explainability
        explanation = self._build_explanation(task, routing_result, all_skills)

        return ExecutionContext(
            task=task,
            skills=skill_contents,
            primary_names=primary_names,
            supporting_names=supporting_names,
            dependency_names=dependency_names,
            verification_plan=verification_plan,
            confidence=routing_result.confidence,
            explanation=explanation,
            token_count=sum(s.estimated_tokens for s in all_skills),
            budget=budget_result,
        )

    def recover(
        self,
        failure_type: str,
        current_skills: list[str],
    ) -> RecoveryContext:
        """Prepare a recovery context after a failure.

        Flow:
            failure_type → classify → route recovery → resolve deps → load content

        Args:
            failure_type: One of the 10 FAILURE_TYPES values.
            current_skills: Skills that were active when the failure occurred.

        Returns:
            Deterministic RecoveryContext with recovery skills and their content.
        """
        # Phase 1: Route recovery
        recovery_result = self.recovery_router.route_recovery(failure_type, current_skills)

        # Phase 2: Resolve dependencies for recovery skills
        all_recovery_names = set(recovery_result.recovery_skills)
        for skill_name in recovery_result.recovery_skills:
            deps = self.router._get_bounded_dependencies(skill_name, 1)
            all_recovery_names.update(deps)
            # Remove current skills from recovery
            all_recovery_names -= set(current_skills)

        # Phase 3: Load content
        recovery_skill_objects = []
        for name in sorted(all_recovery_names):
            skill = self.registry.get_skill(name)
            if skill:
                recovery_skill_objects.append(skill)

        skill_contents = self._load_skill_contents(recovery_skill_objects)

        # Phase 4: Diagnosis
        diagnosis = self.recovery_router.diagnose_failure(failure_type)

        return RecoveryContext(
            failure_type=failure_type,
            recovery_skills=skill_contents,
            confidence=recovery_result.confidence,
            reason=recovery_result.reason,
            diagnosis=diagnosis,
        )

    def _load_skill_contents(self, skills: list[SkillMetadata]) -> list[SkillContent]:
        """Load actual Markdown content for a list of skills.

        Uses existing SkillRegistry.get_skill_content().
        Deterministic: same skills → same order and content.
        """
        contents = []
        for skill in skills:
            content = self.registry.get_skill_content(skill.name)
            if content is not None:
                contents.append(SkillContent(
                    name=skill.name,
                    metadata=skill,
                    content=content,
                ))
        return contents

    def _build_explanation(
        self,
        task: str,
        routing_result,
        all_skills: list[SkillMetadata],
    ) -> RoutingExplanation:
        """Build a routing explanation from the routing result.

        Uses existing ExplainabilityEngine.
        """
        selected = [(s, self.router.get_score(s.name, task)) for s in all_skills]
        all_registry_skills = list(self.registry.get_all_skills())
        excluded = [
            (s, self.router.get_score(s.name, task))
            for s in all_registry_skills
            if self.router.get_score(s.name, task) < 5
            and s.name not in {sk.name for sk in all_skills}
        ][:10]

        return self.explainer.explain_routing(task, selected, excluded)
