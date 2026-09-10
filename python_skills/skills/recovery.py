"""Failure taxonomy and recovery routing."""

from dataclasses import dataclass, field
from .registry import SkillRegistry
from .graph import SkillGraph


# Controlled failure vocabulary
FAILURE_TYPES = {
    "syntax": "Syntax errors, parse failures",
    "type": "Type errors, type mismatches",
    "test": "Test failures, assertion errors",
    "behavior": "Incorrect runtime behavior",
    "security": "Security vulnerabilities, injection attacks",
    "performance": "Performance issues, slowdowns",
    "dependency": "Dependency conflicts, missing packages",
    "compatibility": "Version compatibility issues",
    "configuration": "Configuration errors, missing settings",
    "integration": "Integration failures, API mismatches",
}


@dataclass
class FailureInfo:
    """Information about a failure."""
    failure_type: str
    description: str
    related_skills: list[str] = field(default_factory=list)


@dataclass
class RecoveryResult:
    """Result of recovery routing."""
    failure_type: str
    current_skills: list[str]
    recovery_skills: list[str]
    confidence: str  # HIGH, MEDIUM, LOW
    reason: str


class FailureTaxonomy:
    """Manages failure classification and skill-failure mapping."""

    # Default skill-failure mappings
    SKILL_FAILURE_MAP: dict[str, list[str]] = {
        "sql_injection": ["security", "test"],
        "path_traversal": ["security", "test"],
        "input_validation": ["security", "test", "behavior"],
        "command_injection": ["security", "test"],
        "file_handling": ["security", "behavior"],
        "secrets": ["security", "configuration"],
        "auth_boundaries": ["security", "integration"],
        "unsafe_deserialization": ["security", "test"],
        "dependency_risks": ["dependency", "security"],
        "async_concurrency": ["behavior", "performance", "integration"],
        "database": ["integration", "behavior", "test"],
        "http_clients": ["integration", "behavior", "test"],
        "error_handling": ["behavior", "test"],
        "configuration": ["configuration", "behavior"],
        "dependency_management": ["dependency", "compatibility"],
        "virtual_environments": ["dependency", "configuration"],
        "regression_tests": ["test", "behavior"],
        "safe_refactoring": ["test", "behavior"],
        "edge_cases": ["test", "behavior"],
        "fixtures_mocks": ["test", "integration"],
        "coverage": ["test"],
        "organization": ["test"],
        "parameterized": ["test"],
        "async_tests": ["test", "behavior"],
        "inspection_techniques": ["behavior"],
        "root_cause": ["behavior"],
        "common_bugs": ["behavior", "test"],
    }

    # Recovery skill mappings per failure type
    RECOVERY_MAP: dict[str, list[str]] = {
        "security": ["sql_injection", "input_validation", "path_traversal", "command_injection"],
        "test": ["regression_tests", "edge_cases", "fixtures_mocks"],
        "behavior": ["error_handling", "regression_tests", "inspection_techniques"],
        "dependency": ["dependency_management", "virtual_environments"],
        "compatibility": ["dependency_management", "packaging"],
        "configuration": ["configuration", "environment"],
        "integration": ["http_clients", "database", "async_concurrency"],
        "performance": ["async_concurrency", "database"],
        "syntax": [],
        "type": ["type_hints", "type_annotations"],
    }

    def classify(self, skill_name: str) -> list[str]:
        """Get failure types for a skill."""
        return self.SKILL_FAILURE_MAP.get(skill_name, [])

    def get_recovery_skills(self, failure_type: str, current_skills: list[str]) -> list[str]:
        """Get recovery skills for a failure type, excluding current skills."""
        current_set = set(current_skills)
        candidates = self.RECOVERY_MAP.get(failure_type, [])
        return [s for s in sorted(candidates) if s not in current_set]


class RecoveryRouter:
    """Routes recovery actions based on failure type and current skills."""

    def __init__(self, registry: SkillRegistry, graph: SkillGraph | None = None):
        self.registry = registry
        self.graph = graph or SkillGraph(registry)
        self.graph.build()
        self.taxonomy = FailureTaxonomy()

    def route_recovery(
        self,
        failure_type: str,
        current_skills: list[str],
    ) -> RecoveryResult:
        """Route recovery based on failure type and current skills.

        Algorithm:
        1. Get candidate recovery skills for failure type
        2. Filter out currently active skills
        3. Score candidates against failure context
        4. Select top candidates
        5. Determine confidence level
        """
        # Get recovery candidates
        candidates = self.taxonomy.get_recovery_skills(failure_type, current_skills)

        # Score candidates
        scored: list[tuple[int, str]] = []
        for candidate in candidates:
            score = self._score_recovery_candidate(candidate, failure_type, current_skills)
            scored.append((score, candidate))

        # Sort deterministically: score desc, name asc
        scored.sort(key=lambda x: (-x[0], x[1]))

        # Select top candidates (max 3)
        recovery_skills = [name for _, name in scored[:3]]

        # Determine confidence
        confidence, reason = self._assess_confidence(
            failure_type, current_skills, recovery_skills
        )

        return RecoveryResult(
            failure_type=failure_type,
            current_skills=sorted(current_skills),
            recovery_skills=recovery_skills,
            confidence=confidence,
            reason=reason,
        )

    def _score_recovery_candidate(
        self,
        candidate: str,
        failure_type: str,
        current_skills: list[str],
    ) -> int:
        """Score a recovery candidate."""
        score = 0

        # Check if candidate handles this failure type
        if candidate in self.taxonomy.SKILL_FAILURE_MAP:
            if failure_type in self.taxonomy.SKILL_FAILURE_MAP[candidate]:
                score += 5

        # Check if candidate is related to current skills
        for current in current_skills:
            related = self.graph.get_related(current)
            if candidate in related:
                score += 3

        # Check if candidate depends on current skills
        for current in current_skills:
            deps = self.graph.get_all_dependencies(candidate)
            if current in deps:
                score += 2

        # Priority bonus
        skill = self.registry.get_skill(candidate)
        if skill:
            if skill.priority == "critical":
                score += 2
            elif skill.priority == "high":
                score += 1

        return score

    def _assess_confidence(
        self,
        failure_type: str,
        current_skills: list[str],
        recovery_skills: list[str],
    ) -> tuple[str, str]:
        """Assess confidence in recovery routing."""
        if not recovery_skills:
            return "LOW", "No recovery skills found for this failure type"

        # Check if we have direct failure-type matches
        direct_matches = 0
        for skill in recovery_skills:
            if skill in self.taxonomy.SKILL_FAILURE_MAP:
                if failure_type in self.taxonomy.SKILL_FAILURE_MAP[skill]:
                    direct_matches += 1

        if direct_matches >= 2:
            return "HIGH", f"Multiple skills directly handle {failure_type} failures"
        elif direct_matches == 1:
            return "HIGH", f"Skill directly handles {failure_type} failures"
        elif recovery_skills:
            return "MEDIUM", "Recovery skills are related but don't directly address failure type"
        else:
            return "LOW", "No confident recovery path identified"

    def diagnose_failure(
        self,
        failure_type: str,
        error_message: str | None = None,
    ) -> FailureInfo:
        """Diagnose a failure and suggest relevant skills."""
        description = FAILURE_TYPES.get(failure_type, "Unknown failure type")

        # Find skills that handle this failure type
        related = []
        for skill, failures in self.taxonomy.SKILL_FAILURE_MAP.items():
            if failure_type in failures:
                related.append(skill)

        return FailureInfo(
            failure_type=failure_type,
            description=description,
            related_skills=sorted(related),
        )
