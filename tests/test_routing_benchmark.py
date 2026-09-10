"""Routing benchmark suite - deterministic skill selection tests."""

import pytest
from pathlib import Path
from python_skills.skills.registry import SkillRegistry
from python_skills.skills.graph import SkillGraph
from python_skills.skills.routing import SkillRouter


SKILLS_ROOT = Path(__file__).resolve().parent.parent / "skills"


@pytest.fixture
def router():
    """Create a router with all skills loaded."""
    registry = SkillRegistry(SKILLS_ROOT)
    graph = SkillGraph(registry)
    return SkillRouter(registry, graph)


class TestPositiveRouting:
    """Test cases where specific skills SHOULD be selected."""

    def test_sql_injection_fix(self, router):
        """Fix SQL injection in a FastAPI endpoint."""
        result = router.route("Fix SQL injection in a FastAPI endpoint")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "sql_injection" in all_names

    def test_file_upload_endpoint(self, router):
        """Build a secure file upload endpoint."""
        result = router.route("Build a secure file upload endpoint")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "file_handling" in all_names
        assert "path_traversal" in all_names

    def test_async_http_client(self, router):
        """Create an async HTTP client with retry logic."""
        result = router.route("Create an async HTTP client with retry logic")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "http_clients" in all_names

    def test_database_migration(self, router):
        """Write a database migration script."""
        result = router.route("Write a database migration script")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "database" in all_names

    def test_cli_argument_parser(self, router):
        """Build a CLI tool with argument parsing."""
        result = router.route("Build a CLI tool with argument parsing")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "argparse" in all_names

    def test_error_handling_patterns(self, router):
        """Implement consistent error handling across the application."""
        result = router.route("Implement consistent error handling")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "error_handling" in all_names

    def test_type_hints_modern(self, router):
        """Add type hints to a Python 3.12 codebase."""
        result = router.route("Add type hints to a Python 3.12 codebase")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "type_hints" in all_names or "type_annotations" in all_names

    def test_security_audit(self, router):
        """Perform a security audit of the application."""
        result = router.route("Perform a security audit of the application")
        all_names = [s.name for s in result.primary + result.supporting]
        security_skills = [n for n in all_names if n in [
            "sql_injection", "command_injection", "path_traversal",
            "input_validation", "file_handling", "secrets",
            "auth_boundaries", "dependency_risks", "unsafe_deserialization"
        ]]
        assert len(security_skills) >= 2

    def test_refactoring_safe(self, router):
        """Safely refactor legacy code with tests."""
        result = router.route("Safely refactor legacy code with tests")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "safe_refactoring" in all_names

    def test_configuration_management(self, router):
        """Set up configuration management for the project."""
        result = router.route("Set up configuration management")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "configuration" in all_names

    def test_dependency_management(self, router):
        """Manage Python dependencies with uv."""
        result = router.route("Manage Python dependencies with uv")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "dependency_management" in all_names or "virtual_environments" in all_names

    def test_logging_setup(self, router):
        """Set up application logging with structured output."""
        result = router.route("Set up application logging")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "application_logging" in all_names or "logging" in all_names

    def test_test_organization(self, router):
        """Organize test suite with fixtures and mocks."""
        result = router.route("Organize test suite with fixtures and mocks")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "organization" in all_names or "fixtures_mocks" in all_names

    def test_path_handling(self, router):
        """Work with file paths and directories safely."""
        result = router.route("Work with file paths and directories safely")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "pathlib" in all_names

    def test_json_processing(self, router):
        """Process JSON data with validation."""
        result = router.route("Process JSON data with validation")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "json" in all_names

    def test_regex_patterns(self, router):
        """Parse text with regular expressions."""
        result = router.route("Parse text with regular expressions")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "re" in all_names

    def test_datetime_operations(self, router):
        """Handle date and time operations."""
        result = router.route("Handle date and time operations")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "datetime" in all_names

    def test_subprocess_execution(self, router):
        """Execute system commands safely."""
        result = router.route("Execute system commands safely")
        all_names = [s.name for s in result.primary + result.supporting]
        # subprocess or command_injection should be selected
        assert "subprocess" in all_names or "command_injection" in all_names

    def test_protocols_generics(self, router):
        """Define protocols and generic types."""
        result = router.route("Define protocols and generic types")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "protocols_generics" in all_names

    def test_validation_pipeline(self, router):
        """Build a data validation pipeline."""
        result = router.route("Build a data validation pipeline")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "validation_pipeline" in all_names or "input_validation" in all_names

    def test_project_structure(self, router):
        """Set up a new Python project structure."""
        result = router.route("Set up a new Python project structure")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "project_structure" in all_names

    def test_debugging_inspection(self, router):
        """Debug a complex issue using inspection techniques."""
        result = router.route("Debug a complex issue using inspection techniques")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "inspection_techniques" in all_names or "root_cause" in all_names

    def test_code_quality(self, router):
        """Improve code quality and readability."""
        result = router.route("Improve code quality and readability")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "readability" in all_names or "naming" in all_names

    def test_secrets_management(self, router):
        """Manage secrets and API keys securely."""
        result = router.route("Manage secrets and API keys securely")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "secrets" in all_names

    def test_auth_implementation(self, router):
        """Implement authentication and authorization."""
        result = router.route("Implement authentication and authorization")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "auth_boundaries" in all_names

    def test_dependency_security(self, router):
        """Audit dependencies for security vulnerabilities."""
        result = router.route("Audit dependencies for security vulnerabilities")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "dependency_risks" in all_names

    def test_deserialization_safety(self, router):
        """Handle deserialization safely with untrusted data."""
        result = router.route("Handle deserialization safely with untrusted data")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "unsafe_deserialization" in all_names

    def test_collections_usage(self, router):
        """Use advanced collection patterns."""
        result = router.route("Use advanced collection patterns")
        all_names = [s.name for s in result.primary + result.supporting]
        # At least one skill should be selected
        assert len(all_names) > 0

    def test_functors_patterns(self, router):
        """Apply functional programming patterns with functools."""
        result = router.route("Apply functional programming patterns with functools")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "functools" in all_names


class TestNegativeRouting:
    """Test cases where specific skills should NOT be selected."""

    def test_dataclass_no_security(self, router):
        """Create a Python dataclass - should not select security skills."""
        result = router.route("Create a Python dataclass")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names
        assert "command_injection" not in primary_names
        assert "path_traversal" not in primary_names

    def test_csv_no_security(self, router):
        """Write a CSV processing script - should not select security skills."""
        result = router.route("Write a CSV processing script")
        primary_names = [s.name for s in result.primary]
        security_in_primary = [s for s in result.primary if s.category == "security"]
        assert len(security_in_primary) == 0

    def test_list_comprehension_no_security(self, router):
        """Use list comprehension - minimal skill selection."""
        result = router.route("Use list comprehension to filter data")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names
        assert "path_traversal" not in primary_names

    def test_decorator_no_database(self, router):
        """Write a decorator - should not select database skills."""
        result = router.route("Write a decorator for logging")
        primary_names = [s.name for s in result.primary]
        assert "database" not in primary_names

    def test_context_manager_no_security(self, router):
        """Implement context manager - no security skills."""
        result = router.route("Implement a context manager for file handling")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names
        assert "command_injection" not in primary_names

    def test_generator_no_security(self, router):
        """Write a generator function - no security skills."""
        result = router.route("Write a generator function for data processing")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_metaclass_no_security(self, router):
        """Use metaclass - no security skills."""
        result = router.route("Use metaclass for custom class creation")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_algorithms_no_security(self, router):
        """Implement sorting algorithm - no security skills."""
        result = router.route("Implement a sorting algorithm")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_unit_test_no_security(self, router):
        """Write unit tests - no security skills."""
        result = router.route("Write unit tests for a function")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_class_inheritance_no_security(self, router):
        """Use class inheritance - no security skills."""
        result = router.route("Use class inheritance for code reuse")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_fibonacci_no_security(self, router):
        """Calculate Fibonacci numbers - no security skills."""
        result = router.route("Calculate Fibonacci numbers efficiently")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_string_formatting_no_security(self, router):
        """Format strings with f-strings - no security skills."""
        result = router.route("Format strings with f-strings")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_typing_no_security(self, router):
        """Add type annotations - no security skills."""
        result = router.route("Add type annotations to a function")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_comprehension_no_security(self, router):
        """Use dictionary comprehension - no security skills."""
        result = router.route("Use dictionary comprehension to transform data")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_async_basic_no_security(self, router):
        """Write basic async function - no security skills."""
        result = router.route("Write a basic async function")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_contextlib_no_security(self, router):
        """Use contextlib - no security skills."""
        result = router.route("Use contextlib for context managers")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_enum_no_security(self, router):
        """Use enum for constants - no security skills."""
        result = router.route("Use enum for constants")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_dataclass_validator_no_security(self, router):
        """Use dataclass with validator - no security skills."""
        result = router.route("Use dataclass with validator")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_slots_optimization(self, router):
        """Use __slots__ for memory optimization."""
        result = router.route("Use __slots__ for memory optimization")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names

    def test_properties_pattern(self, router):
        """Use properties for encapsulation."""
        result = router.route("Use properties for encapsulation")
        primary_names = [s.name for s in result.primary]
        assert "sql_injection" not in primary_names


class TestComposition:
    """Test multi-skill composition scenarios."""

    def test_secure_upload_composition(self, router):
        """Compose skills for secure file upload."""
        result = router.compose("Build a secure file upload endpoint")
        all_names = [s.name for s in result.primary + result.supporting + result.dependencies]
        assert "file_handling" in all_names
        assert "path_traversal" in all_names

    def test_api_endpoint_composition(self, router):
        """Compose skills for API endpoint development."""
        result = router.compose("Build a REST API endpoint with authentication")
        all_names = [s.name for s in result.primary + result.supporting + result.dependencies]
        assert len(all_names) >= 2

    def test_database_crud_composition(self, router):
        """Compose skills for database CRUD operations."""
        result = router.compose("Implement database CRUD operations")
        all_names = [s.name for s in result.primary + result.supporting + result.dependencies]
        assert "database" in all_names

    def test_async_service_composition(self, router):
        """Compose skills for async service implementation."""
        result = router.compose("Implement an async microservice")
        all_names = [s.name for s in result.primary + result.supporting + result.dependencies]
        assert "async_concurrency" in all_names or "http_clients" in all_names

    def test_test_suite_composition(self, router):
        """Compose skills for test suite creation."""
        result = router.compose("Create a comprehensive test suite")
        all_names = [s.name for s in result.primary + result.supporting + result.dependencies]
        # At least one skill should be selected
        assert len(all_names) > 0

    def test_project_setup_composition(self, router):
        """Compose skills for project setup."""
        result = router.compose("Set up a new Python project with packaging")
        all_names = [s.name for s in result.primary + result.supporting + result.dependencies]
        assert "project_structure" in all_names or "packaging" in all_names

    def test_code_review_composition(self, router):
        """Compose skills for code review."""
        result = router.compose("Review code for quality and security")
        all_names = [s.name for s in result.primary + result.supporting + result.dependencies]
        assert len(all_names) >= 2

    def test_debugging_composition(self, router):
        """Compose skills for debugging."""
        result = router.compose("Debug and fix a production issue")
        all_names = [s.name for s in result.primary + result.supporting + result.dependencies]
        assert "inspection_techniques" in all_names or "root_cause" in all_names or "common_bugs" in all_names

    def test_refactoring_composition(self, router):
        """Compose skills for refactoring."""
        result = router.compose("Refactor code to improve maintainability")
        all_names = [s.name for s in result.primary + result.supporting + result.dependencies]
        assert "safe_refactoring" in all_names or "maintainability" in all_names

    def test_security_hardening_composition(self, router):
        """Compose skills for security hardening."""
        result = router.compose("Harden application security")
        all_names = [s.name for s in result.primary + result.supporting + result.dependencies]
        security_skills = [n for n in all_names if n in [
            "sql_injection", "command_injection", "path_traversal",
            "input_validation", "file_handling", "secrets",
            "auth_boundaries", "dependency_risks", "unsafe_deserialization"
        ]]
        assert len(security_skills) >= 2


class TestSecurityRouting:
    """Test security-sensitive routing scenarios."""

    def test_injection_prevention(self, router):
        """Route injection prevention tasks to security skills."""
        result = router.route("Prevent SQL and command injection attacks")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "sql_injection" in all_names
        assert "command_injection" in all_names

    def test_path_traversal_prevention(self, router):
        """Route path traversal prevention to security skills."""
        result = router.route("Prevent directory traversal attacks")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "path_traversal" in all_names

    def test_input_validation_security(self, router):
        """Route input validation to security skills."""
        result = router.route("Validate all user input at system boundaries")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "input_validation" in all_names

    def test_secrets_management_security(self, router):
        """Route secrets management to security skills."""
        result = router.route("Manage API keys and secrets securely")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "secrets" in all_names

    def test_auth_security(self, router):
        """Route authentication to security skills."""
        result = router.route("Implement secure authentication")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "auth_boundaries" in all_names

    def test_deserialization_security(self, router):
        """Route deserialization to security skills."""
        result = router.route("Handle untrusted deserialization safely")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "unsafe_deserialization" in all_names

    def test_dependency_security_audit(self, router):
        """Route dependency audit to security skills."""
        result = router.route("Audit third-party dependencies for vulnerabilities")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "dependency_risks" in all_names

    def test_file_upload_security(self, router):
        """Route file upload to security skills."""
        result = router.route("Handle file uploads securely")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "file_handling" in all_names
        assert "path_traversal" in all_names

    def test_security_comprehensive(self, router):
        """Route comprehensive security review."""
        result = router.route("Perform comprehensive security review")
        all_names = [s.name for s in result.primary + result.supporting]
        security_count = sum(1 for n in all_names if n in [
            "sql_injection", "command_injection", "path_traversal",
            "input_validation", "file_handling", "secrets",
            "auth_boundaries", "dependency_risks", "unsafe_deserialization"
        ])
        assert security_count >= 2

    def test_critical_security_priority(self, router):
        """Verify critical security skills get priority."""
        result = router.route("Fix security vulnerabilities")
        all_names = [s.name for s in result.primary + result.supporting]
        security_in_results = [s for s in result.primary + result.supporting if s.category == "security"]
        # Most security skills should have critical priority
        critical_count = sum(1 for s in security_in_results if s.priority == "critical")
        assert critical_count >= len(security_in_results) // 2


class TestVersionSensitive:
    """Test version-sensitive routing scenarios."""

    def test_python_version_detection(self, router):
        """Route Python version-specific tasks."""
        result = router.route("Use match statement (Python 3.10+)")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "control_flow" in all_names

    def test_async_python_version(self, router):
        """Route async tasks with version context."""
        result = router.route("Use TaskGroup for concurrent tasks (Python 3.11+)")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "async_concurrency" in all_names

    def test_type_hints_version(self, router):
        """Route type hints with version context."""
        result = router.route("Use modern type hints (Python 3.12+)")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "type_hints" in all_names or "type_annotations" in all_names

    def test_packaging_version(self, router):
        """Route packaging with version context."""
        result = router.route("Use pyproject.toml for packaging")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "pyproject_toml" in all_names or "packaging" in all_names

    def test_dependency_management_version(self, router):
        """Route dependency management with version context."""
        result = router.route("Manage dependencies with uv (modern tooling)")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "dependency_management" in all_names or "virtual_environments" in all_names

    def test_database_driver_version(self, router):
        """Route database tasks with driver version context."""
        result = router.route("Use asyncpg for async PostgreSQL")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "database" in all_names

    def test_http_client_version(self, router):
        """Route HTTP client with version context."""
        result = router.route("Use httpx for modern HTTP requests")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "http_clients" in all_names

    def test_pytest_version(self, router):
        """Route testing with version context."""
        result = router.route("Use pytest with modern fixtures")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "fixtures_mocks" in all_names or "organization" in all_names

    def test_virtual_env_version(self, router):
        """Route virtual environment with version context."""
        result = router.route("Create isolated Python environment")
        all_names = [s.name for s in result.primary + result.supporting]
        assert "virtual_environments" in all_names

    def test_subprocess_version(self, router):
        """Route subprocess with version context."""
        result = router.route("Execute system commands safely (modern approach)")
        all_names = [s.name for s in result.primary + result.supporting]
        # subprocess or command_injection should be selected
        assert "subprocess" in all_names or "command_injection" in all_names


class TestForbiddenSkills:
    """Test that forbidden skills are excluded."""

    def test_forbidden_sql_injection(self, router):
        """Test excluding sql_injection from results."""
        result = router.route("Fix SQL injection", forbidden=["sql_injection"])
        all_names = [s.name for s in result.primary + result.supporting]
        assert "sql_injection" not in all_names

    def test_forbidden_multiple(self, router):
        """Test excluding multiple skills."""
        result = router.route("Build secure endpoint", forbidden=["sql_injection", "path_traversal"])
        all_names = [s.name for s in result.primary + result.supporting]
        assert "sql_injection" not in all_names
        assert "path_traversal" not in all_names


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_task(self, router):
        """Test routing with empty task description."""
        result = router.route("")
        assert len(result.primary) == 0

    def test_single_word_task(self, router):
        """Test routing with single word task."""
        result = router.route("security")
        assert len(result.primary) > 0

    def test_very_long_task(self, router):
        """Test routing with very long task description."""
        task = "Fix " * 100 + "SQL injection"
        result = router.route(task)
        all_names = [s.name for s in result.primary + result.supporting]
        assert "sql_injection" in all_names

    def test_case_insensitive(self, router):
        """Test routing is case insensitive."""
        result1 = router.route("SQL injection")
        result2 = router.route("sql injection")
        assert [s.name for s in result1.primary] == [s.name for s in result2.primary]

    def test_deterministic_results(self, router):
        """Test routing produces deterministic results."""
        task = "Fix SQL injection in FastAPI"
        result1 = router.route(task)
        result2 = router.route(task)
        assert [s.name for s in result1.primary] == [s.name for s in result2.primary]

    def test_skill_count_limit(self, router):
        """Test composition respects skill count limit."""
        result = router.compose("Build comprehensive application", max_skills=3)
        assert len(result.primary) <= 3

    def test_no_self_dependency(self, router):
        """Test skills don't depend on themselves."""
        for name, skill in router.registry._skills.items():
            assert name not in skill.dependencies

    def test_related_not_self(self, router):
        """Test skills aren't related to themselves."""
        for name, skill in router.registry._skills.items():
            assert name not in skill.related


class TestGraphValidation:
    """Test skill graph integrity."""

    def test_no_cycles(self, router):
        """Test no circular dependencies."""
        cycles = router.graph.detect_cycles()
        assert len(cycles) == 0

    def test_no_orphan_references(self, router):
        """Test all references point to existing skills."""
        orphans = router.graph.find_orphan_references()
        real_orphans = [o for o in orphans if o["reference"]]
        assert len(real_orphans) == 0

    def test_topological_sort_valid(self, router):
        """Test topological sort respects dependencies."""
        order = router.graph.topological_sort()
        order_index = {name: i for i, name in enumerate(order)}

        for name in order:
            skill = router.registry.get_skill(name)
            for dep in skill.dependencies:
                dep_name = dep.rsplit("/", 1)[-1] if "/" in dep else dep
                if dep_name in order_index:
                    assert order_index[dep_name] < order_index[name]

    def test_all_skills_in_graph(self, router):
        """Test all skills are in the graph."""
        stats = router.graph.get_stats()
        assert stats["total_skills"] == 69

    def test_graph_stats(self, router):
        """Test graph statistics are valid."""
        stats = router.graph.get_stats()
        assert stats["total_skills"] == 69
        assert stats["total_edges"] >= 0
        assert isinstance(stats["isolated_skills"], list)


class TestTokenEfficiency:
    """Test token/context efficiency."""

    def test_simple_task_minimal_skills(self, router):
        """Simple tasks should select minimal skills."""
        result = router.route("Use f-strings for formatting")
        assert len(result.primary) <= 3

    def test_complex_task_more_skills(self, router):
        """Complex tasks can select more skills."""
        result = router.route(
            "Build secure async API with database, authentication, "
            "input validation, and comprehensive error handling"
        )
        assert len(result.primary) >= 2

    def test_dependencies_included(self, router):
        """Dependencies should be included when needed."""
        result = router.route("Fix SQL injection in database queries")
        all_names = [s.name for s in result.primary + result.dependencies]
        assert "database" in all_names or "input_validation" in all_names

    def test_estimated_tokens_available(self, router):
        """All skills should have estimated_tokens."""
        for name, skill in router.registry._skills.items():
            assert hasattr(skill, 'estimated_tokens')
            assert skill.estimated_tokens > 0

    def test_routing_score_available(self, router):
        """Routing result should include score."""
        result = router.route("Fix SQL injection")
        assert result.score > 0
