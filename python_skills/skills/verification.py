"""Verification planner - deterministic verification plan generation."""

from dataclasses import dataclass, field
from enum import Enum
from .metadata import SkillMetadata


class VerificationLevel(Enum):
    """Verification levels for skill validation."""
    STATIC = "static"      # Code analysis, linting, type checking
    TEST = "test"          # Unit tests, integration tests
    BEHAVIOR = "behavior"  # Runtime behavior verification
    SECURITY = "security"  # Security-specific validation
    VERSION = "version"    # Version compatibility checks


@dataclass
class VerificationCheck:
    """A single verification check."""
    level: VerificationLevel
    description: str
    skill: str  # Which skill this check relates to
    priority: int = 0  # Higher = more important


@dataclass
class VerificationPlan:
    """Deterministic verification plan for a task."""
    task: str
    checks: list[VerificationCheck] = field(default_factory=list)
    levels: list[VerificationLevel] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)

    def get_checks_by_level(self, level: VerificationLevel) -> list[VerificationCheck]:
        """Get checks for a specific level."""
        return [c for c in self.checks if c.level == level]

    def has_level(self, level: VerificationLevel) -> bool:
        """Check if a verification level is required."""
        return level in self.levels


class VerificationPlanner:
    """Generates deterministic verification plans from selected skills."""

    # Default verification checks per category
    CATEGORY_CHECKS: dict[str, list[tuple[VerificationLevel, str]]] = {
        "security": [
            (VerificationLevel.SECURITY, "Security review of implementation"),
            (VerificationLevel.STATIC, "Static analysis for vulnerabilities"),
            (VerificationLevel.TEST, "Security-focused test coverage"),
        ],
        "testing": [
            (VerificationLevel.TEST, "Test execution and pass rate"),
            (VerificationLevel.BEHAVIOR, "Behavior verification"),
        ],
        "engineering": [
            (VerificationLevel.STATIC, "Code quality checks"),
            (VerificationLevel.TEST, "Integration test coverage"),
        ],
        "generation": [
            (VerificationLevel.STATIC, "Type checking and linting"),
            (VerificationLevel.TEST, "Unit test coverage"),
        ],
        "quality": [
            (VerificationLevel.STATIC, "Code quality metrics"),
        ],
        "refactoring": [
            (VerificationLevel.TEST, "Regression test coverage"),
            (VerificationLevel.BEHAVIOR, "Behavior preservation"),
        ],
        "stdlib": [
            (VerificationLevel.STATIC, "API usage validation"),
        ],
        "debugging": [
            (VerificationLevel.BEHAVIOR, "Issue reproduction"),
            (VerificationLevel.TEST, "Regression test coverage"),
        ],
    }

    # Skill-specific verification overrides
    SKILL_VERIFICATION: dict[str, list[tuple[VerificationLevel, str]]] = {
        "sql_injection": [
            (VerificationLevel.SECURITY, "SQL parameters are bound"),
            (VerificationLevel.SECURITY, "User input is not interpolated in queries"),
            (VerificationLevel.SECURITY, "Malicious input has regression coverage"),
            (VerificationLevel.TEST, "SQL injection regression tests pass"),
        ],
        "path_traversal": [
            (VerificationLevel.SECURITY, "Path is constrained to intended root"),
            (VerificationLevel.SECURITY, "Traversal sequences are rejected safely"),
            (VerificationLevel.SECURITY, "Symlink behavior is handled correctly"),
            (VerificationLevel.TEST, "Path traversal regression tests pass"),
        ],
        "input_validation": [
            (VerificationLevel.SECURITY, "All external input is validated"),
            (VerificationLevel.SECURITY, "Boundary conditions are tested"),
            (VerificationLevel.TEST, "Validation logic has test coverage"),
        ],
        "command_injection": [
            (VerificationLevel.SECURITY, "Shell commands use parameterized execution"),
            (VerificationLevel.SECURITY, "User input is not passed to shell unsanitized"),
            (VerificationLevel.TEST, "Command injection regression tests pass"),
        ],
        "async_concurrency": [
            (VerificationLevel.TEST, "Async tests pass without deadlocks"),
            (VerificationLevel.BEHAVIOR, "Concurrent operations complete correctly"),
            (VerificationLevel.VERSION, "Python version compatibility verified"),
        ],
        "database": [
            (VerificationLevel.TEST, "Database operations are tested"),
            (VerificationLevel.BEHAVIOR, "Connection pooling works correctly"),
            (VerificationLevel.STATIC, "SQL queries are parameterized"),
        ],
        "error_handling": [
            (VerificationLevel.TEST, "Error paths are tested"),
            (VerificationLevel.BEHAVIOR, "Errors are handled gracefully"),
            (VerificationLevel.STATIC, "No bare except clauses"),
        ],
        "http_clients": [
            (VerificationLevel.TEST, "HTTP client operations are tested"),
            (VerificationLevel.BEHAVIOR, "Retry logic works correctly"),
            (VerificationLevel.VERSION, "HTTP library version compatibility"),
        ],
        "configuration": [
            (VerificationLevel.TEST, "Configuration loading is tested"),
            (VerificationLevel.BEHAVIOR, "Default values are correct"),
        ],
        "dependency_management": [
            (VerificationLevel.VERSION, "Dependency versions are compatible"),
            (VerificationLevel.TEST, "Dependencies install correctly"),
        ],
        "regression_tests": [
            (VerificationLevel.TEST, "Regression tests pass"),
            (VerificationLevel.BEHAVIOR, "Previously fixed bugs remain fixed"),
        ],
        "safe_refactoring": [
            (VerificationLevel.TEST, "All tests pass after refactoring"),
            (VerificationLevel.BEHAVIOR, "Behavior is preserved"),
        ],
        "auth_boundaries": [
            (VerificationLevel.SECURITY, "Authentication is enforced"),
            (VerificationLevel.SECURITY, "Authorization checks are in place"),
            (VerificationLevel.TEST, "Auth logic has test coverage"),
        ],
        "secrets": [
            (VerificationLevel.SECURITY, "Secrets are not hardcoded"),
            (VerificationLevel.SECURITY, "Secrets are stored securely"),
        ],
    }

    def plan(self, task: str, skills: list[SkillMetadata]) -> VerificationPlan:
        """Generate a deterministic verification plan for a task.

        Algorithm:
        1. Collect verification levels from all selected skills
        2. Add skill-specific checks
        3. Add category-level checks
        4. Deduplicate and sort deterministically
        """
        plan = VerificationPlan(task=task)
        seen_checks: set[str] = set()
        levels_seen: set[VerificationLevel] = set()

        # Phase 1: Collect from skill metadata
        for skill in skills:
            # Add verification levels from skill metadata
            for level_str in skill.verification_levels:
                try:
                    level = VerificationLevel(level_str)
                    if level not in levels_seen:
                        levels_seen.add(level)
                        plan.levels.append(level)
                except ValueError:
                    pass

            # Add verification items
            for v in skill.verification:
                if v not in seen_checks:
                    seen_checks.add(v)
                    level = self._infer_level(v, skill.category)
                    plan.checks.append(VerificationCheck(
                        level=level,
                        description=v,
                        skill=skill.name,
                    ))

            # Add checks
            for c in skill.checks:
                if c not in seen_checks:
                    seen_checks.add(c)
                    level = self._infer_level(c, skill.category)
                    plan.checks.append(VerificationCheck(
                        level=level,
                        description=c,
                        skill=skill.name,
                    ))

        # Phase 2: Add skill-specific verification
        for skill in skills:
            if skill.name in self.SKILL_VERIFICATION:
                for level, desc in self.SKILL_VERIFICATION[skill.name]:
                    if desc not in seen_checks:
                        seen_checks.add(desc)
                        plan.checks.append(VerificationCheck(
                            level=level,
                            description=desc,
                            skill=skill.name,
                        ))
                        if level not in levels_seen:
                            levels_seen.add(level)
                            plan.levels.append(level)

        # Phase 3: Add category-level checks
        for skill in skills:
            cat_checks = self.CATEGORY_CHECKS.get(skill.category, [])
            for level, desc in cat_checks:
                if desc not in seen_checks:
                    seen_checks.add(desc)
                    plan.checks.append(VerificationCheck(
                        level=level,
                        description=desc,
                        skill=skill.name,
                    ))
                    if level not in levels_seen:
                        levels_seen.add(level)
                        plan.levels.append(level)

        # Phase 4: Sort deterministically
        plan.checks.sort(key=lambda c: (c.level.value, c.skill, c.description))
        plan.levels.sort(key=lambda l: l.value)
        plan.skills = [s.name for s in skills]

        return plan

    def _infer_level(self, text: str, category: str) -> VerificationLevel:
        """Infer verification level from text content."""
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["security", "vulnerability", "injection", "traversal", "auth"]):
            return VerificationLevel.SECURITY
        if any(kw in text_lower for kw in ["test", "coverage", "regression"]):
            return VerificationLevel.TEST
        if any(kw in text_lower for kw in ["static", "lint", "type", "analysis"]):
            return VerificationLevel.STATIC
        if any(kw in text_lower for kw in ["behavior", "runtime", "execution"]):
            return VerificationLevel.BEHAVIOR
        if any(kw in text_lower for kw in ["version", "compatibility", "python"]):
            return VerificationLevel.VERSION
        # Default based on category
        category_defaults = {
            "security": VerificationLevel.SECURITY,
            "testing": VerificationLevel.TEST,
            "engineering": VerificationLevel.STATIC,
            "generation": VerificationLevel.STATIC,
            "quality": VerificationLevel.STATIC,
            "refactoring": VerificationLevel.TEST,
            "stdlib": VerificationLevel.STATIC,
            "debugging": VerificationLevel.BEHAVIOR,
        }
        return category_defaults.get(category, VerificationLevel.TEST)
