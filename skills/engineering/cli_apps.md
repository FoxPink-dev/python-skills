# Engineering: CLI Applications

**Purpose**: Building command-line interfaces with Python.

**When to use**: Creating CLI tools, scripts, or application entry points.

---

## Core Rules

### Entry Points
```toml
# pyproject.toml
[project.scripts]
my-cli = "mypackage.cli:main"
my-other = "mypackage.other:run"
```

### Click (Recommended for Complex CLIs)
```python
import click
from pathlib import Path

@click.group()
@click.version_option()
@click.option("-v", "--verbose", count=True)
@click.pass_context
def cli(ctx: click.Context, verbose: int):
    """My CLI tool."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

@cli.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option("-o", "--output", type=click.Path(path_type=Path))
@click.pass_context
def process(ctx: click.Context, input: Path, output: Path | None):
    """Process a file."""
    verbose = ctx.obj["verbose"]
    if verbose:
        click.echo(f"Processing {input}")
    # ...

@cli.command()
@click.option("--force", is_flag=True)
def clean(force: bool):
    """Clean cache."""
    if not force:
        click.confirm("Delete all cache?", abort=True)
    # ...

if __name__ == "__main__":
    cli()
```

### Typer (Modern, Type-Hint Based)
```python
import typer
from pathlib import Path
from typing_extensions import Annotated

app = typer.Typer()

@app.command()
def process(
    input: Annotated[Path, typer.Argument(exists=True, help="Input file")],
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    verbose: Annotated[int, typer.Option("-v", "--verbose", count=True)] = 0,
):
    """Process a file."""
    if verbose:
        typer.echo(f"Processing {input}")

@app.command()
def clean(force: Annotated[bool, typer.Option("--force", help="Skip confirmation")] = False):
    """Clean cache."""
    if not force:
        typer.confirm("Delete all cache?", abort=True)

if __name__ == "__main__":
    app()
```

### argparse (Stdlib Only)
```python
import argparse
from pathlib import Path

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="my-cli",
        description="Description",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("-v", "--verbose", action="count", default=0)
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    # ...
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Rich (Beautiful Output)
```python
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

console = Console()

console.print("[bold green]Success![/bold green]")
console.print("[red]Error:[/red] Something failed")

table = Table(title="Results")
table.add_column("Name")
table.add_column("Status")
table.add_row("Item 1", "[green]OK[/green]")
table.add_row("Item 2", "[red]FAIL[/red]")
console.print(table)

with Progress() as progress:
    task = progress.add_task("Processing...", total=100)
    for i in range(100):
        progress.update(task, advance=1)
```

---

## When NOT to Use

| Scenario | Why | Better Alternative |
|----------|-----|-------------------|
| Typer for deep nested subcommands | Typer struggles with deep nesting | Use `click` |
| argparse for complex CLIs | No auto-generated help groups | Use `click` |
| Click for 1-3 command scripts | Overhead | Use `argparse` |
| Rich for simple output | Dependency overhead | Use `print()` |

### Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| Missing `--help` | Users can't discover options | Add `--help` / `--version` |
| No exit codes | Scripts fail silently | Use 0=success, 1=error, 130=interrupt |
| Logic in `__main__.py` | Can't test CLI logic | Extract to entry point function |
| Not testing CLI | Broken CLI on changes | Use `CliRunner` / `typer.testing.CliRunner` |
| Global state | Tests interfere | Use context/state passing |

### Anti-Pattern

```python
# NEVER: Logic in __main__.py
# __main__.py
import sys
args = sys.argv[1:]  # Can't test
result = process(args)  # Can't mock

# NEVER: No testing
# No test_cli.py exists

# BETTER: Testable structure
# cli.py
def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    return run(args)

# test_cli.py
from click.testing import CliRunner
def test_process():
    runner = CliRunner()
    result = runner.invoke(cli, ["process", "input.txt"])
    assert result.exit_code == 0
```

| Complexity | Tool |
|------------|------|
| Simple (1-3 commands) | `argparse` (stdlib) |
| Multiple commands, options | `click` |
| Modern, type-hint focused | `typer` |
| Beautiful output needed | `rich` (with any) |
| No dependencies allowed | `argparse` |

---

## Preferred Patterns

```python
# Common structure
# src/mypackage/cli.py

def main(argv: list[str] | None = None) -> int:
    """Entry point for setuptools console_scripts."""
    try:
        # Parse args, run logic
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        logger.exception("Fatal error")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### Subcommand Organization
```
cli.py          # Main entry, creates command group
commands/
  __init__.py   # Imports and registers subcommands
  process.py    # @cli.command() or @app.command()
  clean.py
  config.py
```

---

## Avoid

- Logic in `__main__.py` (use entry point function)
- Global state in CLI module
- Printing directly (use `click.echo`, `typer.echo`, `console.print`)
- No `--help` / `--version`
- Exit codes not meaningful (0=success, 1=error, 130=interrupt)

---

## Validation Considerations

- `my-cli --help` works
- `my-cli --version` shows version
- Invalid args show usage + exit 2
- Tests for each command
- Shell completion (`click`/`typer` support)

---

## Related Skills

- `stdlib/argparse.md`
- `engineering/configuration.md`
- `engineering/packaging.md`
- `generation/error_handling.md`
- `testing/organization.md`