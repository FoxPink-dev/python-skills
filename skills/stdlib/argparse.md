# Stdlib: argparse

**Purpose**: Command-line argument parsing.

**When to use**: CLI applications. For simple scripts, consider `sys.argv` or `click`/`typer` (external).

---

## Core Rules

### Basic Setup
```python
import argparse

parser = argparse.ArgumentParser(
    description="My CLI tool",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # Shows defaults
)

# Positional argument
parser.add_argument("input", type=Path, help="Input file")

# Optional argument
parser.add_argument("-o", "--output", type=Path, help="Output file")
parser.add_argument("-v", "--verbose", action="count", default=0)  # -v, -vv, -vvv

# Flag
parser.add_argument("--force", action="store_true")

# Choice
parser.add_argument("--format", choices=["json", "yaml", "txt"], default="json")

# Type with validation
def positive_int(s):
    v = int(s)
    if v <= 0:
        raise argparse.ArgumentTypeError("Must be positive")
    return v

parser.add_argument("--count", type=positive_int, default=10)

# Append (multiple values)
parser.add_argument("--tags", action="append", default=[])

# Mutually exclusive group
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--fast", action="store_true")
group.add_argument("--thorough", action="store_true")

# Subcommands
subparsers = parser.add_subparsers(dest="command", required=True)
init_parser = subparsers.add_parser("init")
init_parser.add_argument("name")
run_parser = subparsers.add_parser("run")
run_parser.add_argument("--port", type=int, default=8000)

args = parser.parse_args()
```

### Namespace Access
```python
args.input           # Path object
args.output
args.verbose         # 0, 1, 2, 3
args.force           # True/False
args.format          # "json" | "yaml" | "txt"
args.command         # "init" | "run"
args.name            # For init subcommand
```

### Custom Types
```python
# Path validation
def existing_file(s):
    path = Path(s)
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"Not a file: {s}")
    return path

parser.add_argument("file", type=existing_file)

# Comma-separated list
def csv_list(s):
    return [x.strip() for x in s.split(",") if x.strip()]

parser.add_argument("--tags", type=csv_list, default=[])
```

### Subcommand Pattern (Recommended)
```python
def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # Dispatch to handler
    handlers = {
        "init": handle_init,
        "run": handle_run,
    }
    return handlers[args.command](args)

def handle_init(args):
    print(f"Initializing {args.name}")

def handle_run(args):
    print(f"Running on port {args.port}")

if __name__ == "__main__":
    sys.exit(main())
```

---

## Decision Rules

| Need | Pattern |
|------|---------|
| Required input | Positional argument |
| Optional with default | `--option` with `default` |
| Boolean flag | `action="store_true"` |
| Count verbosity | `action="count"` |
| Multiple values | `action="append"` or `nargs="*"` |
| Choice validation | `choices=[...]` |
| Custom validation | `type=callable` |
| Subcommands | `add_subparsers()` |
| Mutually exclusive | `add_mutually_exclusive_group()` |

---

## Preferred Patterns

```python
# Main entry point pattern
def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mytool",
        description="Description",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # ... add arguments
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    return dispatch(args)

if __name__ == "__main__":
    sys.exit(main())
```

---

## Avoid

- `sys.argv` parsing manually (error-prone)
- Global parser state
- Complex logic in `type=` callables (keep simple)
- Required optional arguments (confusing UX)
- Too many positional arguments (>2-3)

---

## Validation Considerations

- `parser.parse_args(["--help"])` exits 0
- Invalid args exit 2 with usage
- Test with `argv` parameter for unit testing
- `ArgumentDefaultsHelpFormatter` shows defaults in help

---

## Related Skills

- `engineering/cli_apps.md`
- `engineering/configuration.md`
- `stdlib/os_sys.md`
- `generation/type_hints.md`