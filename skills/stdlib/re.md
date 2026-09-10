---
name: re
purpose: Pattern matching and text processing.
category: stdlib
triggers:
  - regex
  - re
  - pattern
  - match
  - search
  - sub
  - compile
dependencies: []
related: []
priority: supporting
estimated_tokens: 1000
---
# Stdlib: re (Regular Expressions)

**Purpose**: Pattern matching and text processing.

**When to use**: String validation, extraction, transformation. Not for parsing structured formats (HTML, JSON, etc.).

---

## Core Rules

### Basic Usage
```python
import re

# Compile once, use many (performance)
PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")

# Match at start
PATTERN.match("2024-01-15")      # Match object or None
PATTERN.match("2024-01-15 text") # Matches!

# Search anywhere
PATTERN.search("Date: 2024-01-15")  # Match object or None

# Full match (entire string)
PATTERN.fullmatch("2024-01-15")    # Match object or None

# Find all
PATTERN.findall("2024-01-15 and 2024-02-20")  # List of strings/groups
PATTERN.finditer("...")           # Iterator of Match objects

# Substitute
PATTERN.sub("REDACTED", text)     # Replace all
PATTERN.subn("REDACTED", text)    # (new_string, count)

# Split
PATTERN.split("a2024-01-15b")     # ["a", "b"]
```

### Match Object
```python
m = PATTERN.search("Date: 2024-01-15")
if m:
    m.group()        # Entire match
    m.group(1)       # Group 1
    m.groups()       # All groups tuple
    m.groupdict()    # Named groups dict
    m.start(), m.end()  # Span
    m.span(1)        # Span of group 1
```

### Common Patterns
```python
# Email (simplified)
r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# URL
r"https?://[^\s/$.?#].[^\s]*"

# IP address
r"\b(?:\d{1,3}\.){3}\d{1,3}\b"

# UUID
r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

# ISO datetime
r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?"
```

### Flags
```python
re.IGNORECASE / re.I     # Case insensitive
re.MULTILINE / re.M      # ^ $ match line start/end
re.DOTALL / re.S         # . matches newline
re.VERBOSE / re.X        # Verbose mode (whitespace ignored, comments)
re.ASCII / re.A          # \w, \d, \s ASCII only
```

### Verbose Mode (Readable)
```python
EMAIL_PATTERN = re.compile(r"""
    [a-zA-Z0-9._%+-]+   # Local part
    @                   # Separator
    [a-zA-Z0-9.-]+      # Domain
    \.[a-zA-Z]{2,}      # TLD
""", re.VERBOSE)
```

### Raw Strings (Critical)
```python
# ALWAYS use raw strings for regex
r"\d+"     # Correct: backslash preserved
"\d+"      # Wrong: "\d" = "d" in string literal
```

---

## Decision Rules

| Need | Method |
|------|--------|
| Validate entire string | `fullmatch` |
| Find first occurrence | `search` |
| Check prefix | `match` |
| Extract all occurrences | `findall` / `finditer` |
| Replace all | `sub` |
| Replace with function | `sub(lambda m: ...)` |
| Split on pattern | `split` |

---

## Preferred Patterns

```python
# Compile at module level (not in function)
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def is_valid_date(s: str) -> bool:
    return ISO_DATE.fullmatch(s) is not None

# Named groups for clarity
LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"
    r"\s+"
    r"(?P<level>\w+)"
    r"\s+"
    r"(?P<message>.*)"
)

for match in LOG_PATTERN.finditer(log_text):
    print(match.groupdict())

# Substitution with function
def redact_emails(text: str) -> str:
    return EMAIL_PATTERN.sub(lambda m: f"{m.group(1)}@[REDACTED]", text)
```

---

## Avoid

- Regex for parsing HTML/XML/JSON (use proper parsers)
- Complex regex without `re.VERBOSE` and comments
- `.*` greedy matching when `.*?` non-greedy needed
- Not using raw strings (`r"..."`)
- Compiling regex inside hot loops
- Catastrophic backtracking (nested quantifiers: `(a+)+`)

---

## Performance

- Compile once, reuse
- `fullmatch` > `match` + `$` > `search` + `^...$`
- `finditer` > `findall` for large data (memory)
- Specific patterns faster than generic

---

## Validation Considerations

- `re.compile` validates pattern syntax at compile time
- Type checkers don't validate regex patterns
- Test edge cases: empty string, no match, multiple matches

---

## Related Skills

- `security/input_validation.md`
- `generation/type_hints.md` (Pattern type)