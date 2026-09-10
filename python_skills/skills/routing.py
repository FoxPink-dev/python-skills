"""Task-to-skill routing - deterministic skill selection based on task description."""

from dataclasses import dataclass, field
from .registry import SkillRegistry
from .metadata import SkillMetadata
from .graph import SkillGraph


@dataclass
class RoutingResult:
    """Result of routing a task to skills."""
    primary: list[SkillMetadata] = field(default_factory=list)
    supporting: list[SkillMetadata] = field(default_factory=list)
    dependencies: list[SkillMetadata] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)
    score: int = 0


class SkillRouter:
    """Deterministic router for task-to-skill mapping."""

    def __init__(self, registry: SkillRegistry, graph: SkillGraph | None = None):
        self.registry = registry
        self.graph = graph or SkillGraph(registry)
        self.graph.build()

    def route(self, task: str, forbidden: list[str] | None = None) -> RoutingResult:
        """Route a task to relevant skills.

        Algorithm:
        1. Score all skills against task keywords
        2. Select primary skills (highest score, explicit match)
        3. Select supporting skills (secondary matches)
        4. Include dependencies of primary skills
        5. Exclude forbidden skills

        Deterministic tie-breaking: alphabetical by name.
        """
        forbidden = set(forbidden or [])
        task_lower = task.lower()

        # Phase 1: Score all skills
        scored: list[tuple[int, str, SkillMetadata]] = []
        for name, skill in self.registry._skills.items():
            if name in forbidden:
                continue
            score = self._score_skill(skill, task_lower)
            if score > 0:
                scored.append((score, name, skill))

        # Sort by score descending, then name ascending (deterministic)
        scored.sort(key=lambda x: (-x[0], x[1]))

        # Phase 2: Select primary skills (score >= 5)
        primary = []
        seen = set()
        for score, name, skill in scored:
            if score >= 5 and name not in seen:
                primary.append(skill)
                seen.add(name)

        # Phase 3: Select supporting skills (score >= 2, not primary)
        supporting = []
        for score, name, skill in scored:
            if score >= 2 and name not in seen and name not in forbidden:
                supporting.append(skill)
                seen.add(name)

        # Phase 4: Include dependencies of primary skills
        dep_names = set()
        for skill in primary:
            deps = self.graph.get_all_dependencies(skill.name)
            dep_names.update(deps)

        dependencies = []
        for dep_name in sorted(dep_names):  # Sorted for determinism
            if dep_name not in seen and dep_name not in forbidden:
                dep_skill = self.registry.get_skill(dep_name)
                if dep_skill:
                    dependencies.append(dep_skill)
                    seen.add(dep_name)

        # Calculate total score
        total_score = sum(self._score_skill(s, task_lower) for s in primary)

        return RoutingResult(
            primary=primary,
            supporting=supporting,
            dependencies=dependencies,
            forbidden=sorted(forbidden),
            score=total_score
        )

    def _score_skill(self, skill: SkillMetadata, task_lower: str) -> int:
        """Score a skill against a task description.

        Scoring:
        - Exact name match in task: 10 points
        - Trigger match: 3 points per trigger
        - Category match: 2 points
        - Description keyword match: 1 point per keyword (>3 chars)
        - Priority bonus: critical=2, high=1, primary=0
        """
        score = 0

        # Exact name match
        if skill.name.lower() in task_lower:
            score += 10

        # Trigger matches
        for trigger in skill.triggers:
            if trigger.lower() in task_lower:
                score += 3

        # Category match
        if skill.category.lower() in task_lower:
            score += 2

        # Description keyword matches
        for word in skill.description.lower().split():
            if len(word) > 3 and word in task_lower:
                score += 1

        # Priority bonus
        if skill.priority == "critical":
            score += 2
        elif skill.priority == "high":
            score += 1

        return score

    def compose(self, task: str, max_skills: int = 5) -> RoutingResult:
        """Compose a minimal set of skills for a task.

        More selective than route() - only includes skills that are
        truly necessary, not just related.
        """
        result = self.route(task)

        # If we have too many skills, keep only primary + their direct deps
        if len(result.primary) > max_skills:
            result.primary = result.primary[:max_skills]
            result.supporting = []

        # Recompute dependencies for trimmed primary
        dep_names = set()
        for skill in result.primary:
            deps = self.graph.get_dependencies(skill.name)
            dep_names.update(deps)

        result.dependencies = []
        seen = {s.name for s in result.primary}
        for dep_name in sorted(dep_names):
            if dep_name not in seen:
                dep_skill = self.registry.get_skill(dep_name)
                if dep_skill:
                    result.dependencies.append(dep_skill)
                    seen.add(dep_name)

        return result

    def is_relevant(self, skill_name: str, task: str, threshold: int = 3) -> bool:
        """Check if a skill is relevant to a task."""
        skill = self.registry.get_skill(skill_name)
        if not skill:
            return False
        return self._score_skill(skill, task.lower()) >= threshold
