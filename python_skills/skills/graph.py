"""Skill graph - dependency analysis, cycle detection, and composition."""

from dataclasses import dataclass, field
from .registry import SkillRegistry


@dataclass
class SkillGraph:
    """Graph of skills with dependencies and relationships."""
    registry: SkillRegistry
    _adjacency: dict[str, set[str]] = field(default_factory=dict)
    _reverse: dict[str, set[str]] = field(default_factory=dict)
    _built: bool = False

    def build(self) -> None:
        """Build the skill graph from registry metadata."""
        if self._built:
            return

        self.registry.load_all()
        self._adjacency = {}
        self._reverse = {}

        for name, skill in self.registry._skills.items():
            self._adjacency[name] = set()
            self._reverse[name] = set()

        for name, skill in self.registry._skills.items():
            # Add dependency edges (skill depends on dep)
            for dep in skill.dependencies:
                dep_name = dep.rsplit("/", 1)[-1] if "/" in dep else dep
                if dep_name in self._adjacency:
                    self._adjacency[name].add(dep_name)
                    self._reverse[dep_name].add(name)

            # Add related edges (bidirectional for graph traversal)
            for rel in skill.related:
                rel_name = rel.rsplit("/", 1)[-1] if "/" in rel else rel
                if rel_name in self._adjacency:
                    # Related is softer than dependency - mark differently
                    pass  # We don't add related to adjacency for cycle detection

        self._built = True

    def get_dependencies(self, name: str) -> set[str]:
        """Get direct dependencies of a skill."""
        if not self._built:
            self.build()
        return self._adjacency.get(name, set())

    def get_all_dependencies(self, name: str) -> set[str]:
        """Get all transitive dependencies of a skill (BFS)."""
        if not self._built:
            self.build()

        visited = set()
        queue = [name]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            for dep in self._adjacency.get(current, set()):
                if dep not in visited:
                    queue.append(dep)
        visited.discard(name)
        return visited

    def get_dependents(self, name: str) -> set[str]:
        """Get skills that depend on this skill."""
        if not self._built:
            self.build()
        return self._reverse.get(name, set())

    def get_related(self, name: str) -> set[str]:
        """Get skills related to this skill."""
        if not self._built:
            self.build()
        skill = self.registry.get_skill(name)
        if not skill:
            return set()
        related = set()
        for rel in skill.related:
            rel_name = rel.rsplit("/", 1)[-1] if "/" in rel else rel
            if rel_name in self._adjacency:
                related.add(rel_name)
        return related

    def detect_cycles(self) -> list[list[str]]:
        """Detect cycles in the dependency graph."""
        if not self._built:
            self.build()

        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self._adjacency.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path)
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(node)

        for node in self._adjacency:
            if node not in visited:
                dfs(node, [])

        return cycles

    def find_orphan_references(self) -> list[dict]:
        """Find references to nonexistent skills."""
        if not self._built:
            self.build()

        orphans = []
        all_skills = set(self._adjacency.keys())

        for name, skill in self.registry._skills.items():
            for dep in skill.dependencies:
                dep_name = dep.rsplit("/", 1)[-1] if "/" in dep else dep
                if dep_name not in all_skills:
                    orphans.append({
                        "skill": name,
                        "field": "dependencies",
                        "reference": dep
                    })

            for rel in skill.related:
                rel_name = rel.rsplit("/", 1)[-1] if "/" in rel else rel
                if rel_name not in all_skills:
                    orphans.append({
                        "skill": name,
                        "field": "related",
                        "reference": rel
                    })

        return orphans

    def topological_sort(self) -> list[str]:
        """Return skills in topological order (dependencies first)."""
        if not self._built:
            self.build()

        visited = set()
        order = []

        def dfs(node: str) -> None:
            visited.add(node)
            for dep in self._adjacency.get(node, set()):
                if dep not in visited:
                    dfs(dep)
            order.append(node)

        for node in self._adjacency:
            if node not in visited:
                dfs(node)

        return order

    def get_stats(self) -> dict:
        """Get graph statistics."""
        if not self._built:
            self.build()

        total_edges = sum(len(deps) for deps in self._adjacency.values())
        isolated = [n for n, deps in self._adjacency.items() if not deps and not self._reverse.get(n)]

        return {
            "total_skills": len(self._adjacency),
            "total_edges": total_edges,
            "isolated_skills": isolated,
            "cycles": self.detect_cycles(),
            "orphans": self.find_orphan_references()
        }
