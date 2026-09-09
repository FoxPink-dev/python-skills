"""CLI for python-skills."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from python_skills.config import InstallConfig, Scope, Target
from python_skills.detector import EnvironmentDetector
from python_skills.installer import SkillInstaller

console = Console()


@click.group()
@click.option("--project-root", "-p", type=click.Path(exists=True, file_okay=False, path_type=Path),
              default=".", help="Project root directory")
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
@click.pass_context
def main(ctx: click.Context, project_root: Path, dry_run: bool):
    """Python Skills - Python engineering skills for AI coding agents."""
    ctx.ensure_object(dict)
    ctx.obj["project_root"] = project_root
    ctx.obj["dry_run"] = dry_run


@main.command()
@click.option("--target", "-t", multiple=True,
              type=click.Choice([t.value for t in Target], case_sensitive=False),
              help="Target AI coding agent(s)")
@click.option("--scope", "-s", type=click.Choice([s.value for s in Scope], case_sensitive=False),
              default="project", help="Installation scope")
@click.option("--auto/--no-auto", default=False, help="Auto-detect and install all compatible targets")
@click.pass_context
def install(ctx: click.Context, target: list[str], scope: str, auto: bool):
    """Install python-skills for AI coding agents."""
    project_root = ctx.obj["project_root"]
    dry_run = ctx.obj["dry_run"]
    scope_enum = Scope(scope)

    console.print(Panel.fit(
        f"[bold]Python Skills Installer[/bold]\n"
        f"Project: {project_root}\n"
        f"Scope: {scope}\n"
        f"Dry run: {dry_run}",
        title="Installation"
    ))

    # Parse targets
    targets = [Target(t.lower()) for t in target] if target else None

    # Create config
    config = InstallConfig(
        targets=targets or [],
        scope=scope_enum,
        dry_run=dry_run
    )

    # Create installer
    installer = SkillInstaller(project_root, config)

    # Detect environments
    detection = installer.detect_environments()

    # Print detection results
    table = Table(title="Environment Detection")
    table.add_column("Target", style="cyan")
    table.add_column("Application", style="green")
    table.add_column("Project Config", style="yellow")
    table.add_column("Details", style="dim")

    for name, result in detection.targets.items():
        app_status = "Yes" if result.application_detected else "No"
        proj_status = "Yes" if result.project_config_detected else "No"
        table.add_row(name, app_status, proj_status, result.details)

    console.print(table)
    console.print()

    # Plan installation
    plan = installer.plan_installation(
        targets=targets,
        scope=scope_enum,
        auto=auto
    )

    if not plan.targets:
        console.print("[yellow]No targets to install[/yellow]")
        return

    # Print plan
    plan_table = Table(title="Installation Plan")
    plan_table.add_column("Target", style="cyan")
    plan_table.add_column("Scope", style="green")
    plan_table.add_column("Dry Run", style="yellow")

    for target, scope_val in plan.targets.items():
        plan_table.add_row(target.value, scope_val.value, "Yes" if plan.dry_run else "No")

    console.print(plan_table)
    console.print()

    if dry_run:
        console.print("[yellow]DRY RUN - No changes will be made[/yellow]")
        return

    # Confirm
    if not click.confirm("Proceed with installation?"):
        console.print("[red]Installation cancelled[/red]")
        return

    # Execute installation
    console.print("\n[bold]Installing...[/bold]")
    results = installer.execute_install(plan)

    # Summary
    success_count = sum(1 for r in results.values() if r.success)
    total_count = len(results)

    console.print(f"\n[bold]Installation complete: {success_count}/{total_count} successful[/bold]")

    if success_count < total_count:
        sys.exit(1)


@main.command()
@click.option("--target", "-t", multiple=True,
              type=click.Choice([t.value for t in Target], case_sensitive=False),
              help="Target(s) to sync")
@click.option("--scope", "-s", type=click.Choice([s.value for s in Scope], case_sensitive=False),
              default="project", help="Sync scope")
@click.pass_context
def sync(ctx: click.Context, target: list[str], scope: str):
    """Sync python-skills with current canonical skills."""
    project_root = ctx.obj["project_root"]
    dry_run = ctx.obj["dry_run"]
    scope_enum = Scope(scope)

    console.print(Panel.fit(
        f"[bold]Python Skills Sync[/bold]\n"
        f"Project: {project_root}\n"
        f"Scope: {scope}\n"
        f"Dry run: {dry_run}",
        title="Sync"
    ))

    config = InstallConfig(targets=[], scope=scope_enum, dry_run=dry_run)
    installer = SkillInstaller(project_root, config)

    targets = [Target(t.lower()) for t in target] if target else None

    if dry_run:
        console.print("[yellow]DRY RUN - No changes will be made[/yellow]")

    console.print("\n[bold]Syncing...[/bold]")
    results = installer.run_sync(scope=scope_enum, targets=targets, dry_run=dry_run)

    # Summary
    success_count = sum(1 for r in results.values() if r.success)
    total_count = len(results)

    console.print(f"\n[bold]Sync complete: {success_count}/{total_count} successful[/bold]")

    if success_count < total_count:
        sys.exit(1)


@main.command()
@click.option("--target", "-t", multiple=True,
              type=click.Choice([t.value for t in Target], case_sensitive=False),
              help="Target(s) to uninstall")
@click.option("--scope", "-s", type=click.Choice([s.value for s in Scope], case_sensitive=False),
              default="project", help="Uninstall scope")
@click.pass_context
def uninstall(ctx: click.Context, target: list[str], scope: str):
    """Uninstall python-skills for AI coding agents."""
    project_root = ctx.obj["project_root"]
    dry_run = ctx.obj["dry_run"]
    scope_enum = Scope(scope)

    console.print(Panel.fit(
        f"[bold]Python Skills Uninstaller[/bold]\n"
        f"Project: {project_root}\n"
        f"Scope: {scope}\n"
        f"Dry run: {dry_run}",
        title="Uninstallation"
    ))

    targets = [Target(t.lower()) for t in target] if target else None

    config = InstallConfig(targets=targets or [], scope=scope_enum, dry_run=dry_run)
    installer = SkillInstaller(project_root, config)

    if dry_run:
        console.print("[yellow]DRY RUN - No changes will be made[/yellow]")

    console.print("\n[bold]Uninstalling...[/bold]")
    results = installer.run_uninstall(scope=scope_enum, targets=targets, dry_run=dry_run)

    success_count = sum(1 for r in results.values() if r.success)
    total_count = len(results)

    console.print(f"\n[bold]Uninstallation complete: {success_count}/{total_count} successful[/bold]")

    if success_count < total_count:
        sys.exit(1)


@main.command()
@click.option("--scope", "-s", type=click.Choice([s.value for s in Scope], case_sensitive=False),
              default="project", help="Status scope")
@click.pass_context
def status(ctx: click.Context, scope: str):
    """Show installation status."""
    project_root = ctx.obj["project_root"]
    scope_enum = Scope(scope)

    console.print(Panel.fit(
        f"[bold]Python Skills Status[/bold]\n"
        f"Project: {project_root}\n"
        f"Scope: {scope}",
        title="Status"
    ))

    config = InstallConfig(targets=[], scope=scope_enum, dry_run=False)
    installer = SkillInstaller(project_root, config)

    console.print("\n[bold]Installation Status[/bold]")
    results = installer.get_status(scope=scope_enum)

    # Summary table
    table = Table()
    table.add_column("Target", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Files", style="yellow")

    for name, result in results.items():
        status = "Installed" if result.installed else "Not installed"
        table.add_row(name, status, str(len(result.files)))

    console.print(table)


@main.command()
@click.option("--scope", "-s", type=click.Choice([s.value for s in Scope], case_sensitive=False),
              default="project", help="Detection scope")
@click.option("--project-root", "-p", type=click.Path(exists=True, file_okay=False, path_type=Path),
              default=".", help="Project root directory")
@click.pass_context
def detect(ctx: click.Context, scope: str, project_root: Path):
    """Detect AI coding agent environments."""
    scope_enum = Scope(scope)

    console.print(Panel.fit(
        f"[bold]Environment Detection[/bold]\n"
        f"Project: {project_root}\n"
        f"Scope: {scope}",
        title="Detection"
    ))

    detector = EnvironmentDetector(project_root)
    detection = detector.detect_all()

    table = Table(title="Environment Detection Results")
    table.add_column("Target", style="cyan")
    table.add_column("Application", style="green")
    table.add_column("Project Config", style="yellow")
    table.add_column("Global Config", style="blue")
    table.add_column("Details", style="dim")

    for name, result in detection.targets.items():
        app = "Yes" if result.application_detected else "No"
        proj = "Yes" if result.project_config_detected else "No"
        glob = "Yes" if (result.details and "Global: yes" in result.details) else "No"
        table.add_row(name, app, proj, glob, result.details)

    console.print(table)


@main.command()
@click.option("--category", "-c", help="Filter by category")
def list(category: str):
    """List available skills and supported targets."""
    from python_skills.skills.registry import get_registry

    registry = get_registry()

    # List targets
    console.print(Panel.fit(
        "[bold]Supported Targets (16)[/bold]\n"
        + "\n".join(f"  {t.value}" for t in Target),
        title="Targets"
    ))

    # List skills
    if category:
        skills = registry.get_skills_by_category(category)
        title = f"Skills in '{category}'"
    else:
        skills = registry.get_all_skills()
        title = f"All Skills ({len(skills)})"

    table = Table(title=title)
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Description", style="dim")

    for skill in sorted(skills, key=lambda s: s.name):
        desc = skill.description[:60] + "..." if len(skill.description) > 60 else skill.description
        table.add_row(skill.name, skill.category, desc)

    console.print(table)


@main.command()
def version():
    """Show version."""
    from python_skills import __version__
    console.print(f"python-skills v{__version__}")


if __name__ == "__main__":
    main()
