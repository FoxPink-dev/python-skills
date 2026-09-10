"""Confidence assessment and explainability for routing decisions."""

from dataclasses import dataclass, field
from .metadata import SkillMetadata


class ConfidenceLevel:
    """Confidence levels for routing decisions."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class SkillExplanation:
    """Explanation for why a skill was selected or excluded."""
    skill: str
    selected: bool
    score: int
    reasons: list[str] = field(default_factory=list)
    confidence: str = ConfidenceLevel.LOW
    dependency_of: list[str] = field(default_factory=list)


@dataclass
class RoutingExplanation:
    """Full explanation of a routing decision."""
    task: str
    selected_skills: list[SkillExplanation] = field(default_factory=list)
    excluded_skills: list[SkillExplanation] = field(default_factory=list)
    total_score: int = 0


class ConfidenceAssessor:
    """Assesses confidence in routing decisions."""

    def assess(self, skill: SkillMetadata, score: int, task: str) -> str:
        """Assess confidence level for a skill selection.

        Rules:
        - Exact name match in task → HIGH
        - Strong trigger match (≥2 triggers) → HIGH
        - Single trigger match → MEDIUM
        - Only description/keyword match → LOW
        """
        task_lower = task.lower()

        # Exact name match
        if skill.name.lower() in task_lower:
            return ConfidenceLevel.HIGH

        # Count trigger matches
        trigger_matches = sum(1 for t in skill.triggers if t.lower() in task_lower)
        if trigger_matches >= 2:
            return ConfidenceLevel.HIGH
        elif trigger_matches == 1:
            return ConfidenceLevel.MEDIUM

        # Category match with priority
        if skill.category.lower() in task_lower and skill.priority in ("critical", "high"):
            return ConfidenceLevel.MEDIUM

        # Low confidence - only description/keyword match
        if score < 5:
            return ConfidenceLevel.LOW

        return ConfidenceLevel.MEDIUM


class ExplainabilityEngine:
    """Generates explanations for routing decisions."""

    def __init__(self):
        self.assessor = ConfidenceAssessor()

    def explain_selection(
        self,
        skill: SkillMetadata,
        score: int,
        task: str,
        dependency_of: list[str] | None = None,
    ) -> SkillExplanation:
        """Explain why a skill was selected."""
        reasons = []
        task_lower = task.lower()

        # Name match
        if skill.name.lower() in task_lower:
            reasons.append(f"trigger match: \"{skill.name}\"")
            reasons.append("explicit name match in task")

        # Trigger matches
        matched_triggers = [t for t in skill.triggers if t.lower() in task_lower]
        if matched_triggers:
            reasons.append(f"trigger match: {', '.join(matched_triggers)}")

        # Category match
        if skill.category.lower() in task_lower:
            reasons.append(f"category match: {skill.category}")

        # Priority
        if skill.priority == "critical":
            reasons.append("priority: critical")
        elif skill.priority == "high":
            reasons.append("priority: high")

        # Dependency relationship
        if dependency_of:
            reasons.append(f"dependency of: {', '.join(sorted(dependency_of))}")

        # Confidence
        confidence = self.assessor.assess(skill, score, task)

        return SkillExplanation(
            skill=skill.name,
            selected=True,
            score=score,
            reasons=reasons,
            confidence=confidence,
            dependency_of=dependency_of or [],
        )

    def explain_exclusion(
        self,
        skill: SkillMetadata,
        score: int,
        task: str,
        reason: str = "below selection threshold",
    ) -> SkillExplanation:
        """Explain why a skill was excluded."""
        reasons = [reason]

        if score == 0:
            reasons.append("no trigger matches")
            reasons.append("no category match")
        elif score < 5:
            reasons.append(f"score {score} below threshold 5")

        return SkillExplanation(
            skill=skill.name,
            selected=False,
            score=score,
            reasons=reasons,
            confidence=ConfidenceLevel.LOW,
        )

    def explain_routing(
        self,
        task: str,
        selected: list[tuple[SkillMetadata, int]],
        excluded: list[tuple[SkillMetadata, int]],
        dependency_of: dict[str, list[str]] | None = None,
    ) -> RoutingExplanation:
        """Generate full routing explanation."""
        dependency_of = dependency_of or {}

        explanation = RoutingExplanation(task=task)

        # Explain selected skills
        for skill, score in selected:
            dep_of = dependency_of.get(skill.name, [])
            explanation.selected_skills.append(
                self.explain_selection(skill, score, task, dep_of)
            )
            explanation.total_score += score

        # Explain excluded skills (top 10 by score for brevity)
        for skill, score in sorted(excluded, key=lambda x: -x[1])[:10]:
            explanation.excluded_skills.append(
                self.explain_exclusion(skill, score, task)
            )

        # Sort deterministically
        explanation.selected_skills.sort(key=lambda e: (-e.score, e.skill))
        explanation.excluded_skills.sort(key=lambda e: (-e.score, e.skill))

        return explanation
