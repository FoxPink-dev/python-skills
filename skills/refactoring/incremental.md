# Refactoring: Incremental Changes

**Purpose**: Make refactoring safe through small, verifiable increments.

**When to use**: Any refactoring larger than a single function extraction.

---

## Core Rules

### Incremental Principles
1. **One logical change per commit**
2. **Each commit passes all tests**
3. **No "temporary" broken state committed**
4. **Reviewable diffs** (<200 lines ideal)

### Breaking Down Large Refactors

```python
# Goal: Replace legacy UserService with NewUserService

# Step 1: Create NewUserService with same interface
class NewUserService:
    def get(self, id): ...
    def create(self, data): ...

# Step 2: Add feature flag
class UserService:
    def __init__(self):
        self.legacy = LegacyUserService()
        self.new = NewUserService()
        self.use_new = settings.use_new_service
    
    def get(self, id):
        if self.use_new:
            return self.new.get(id)
        return self.legacy.get(id)
    
    def create(self, data):
        if self.use_new:
            return self.new.create(data)
        return self.legacy.create(data)

# Step 3: Enable for 1% of users (canary)
# Step 4: Enable for all
# Step 5: Remove legacy code
```

### Incremental Extraction
```python
# Large function -> small functions (one at a time)

# Original: 100-line process() function

# Commit 1: Extract validation
def validate_input(data):
    # ... 20 lines extracted
    pass

def process(data):
    validate_input(data)  # New call
    # ... 80 lines remain

# Commit 2: Extract calculation
def calculate_totals(items):
    # ... 30 lines extracted
    pass

def process(data):
    validate_input(data)
    totals = calculate_totals(data.items)  # New call
    # ... 50 lines remain

# Commit 3: Extract persistence
def save_results(data, totals):
    # ... 30 lines extracted
    pass

def process(data):
    validate_input(data)
    totals = calculate_totals(data.items)
    save_results(data, totals)
    # ... 20 lines remain (orchestration)
```

### Incremental Type Changes
```python
# Change function signature incrementally

# Before: func(a, b, c)
# Goal: func(config: Config)

# Step 1: Add config parameter with defaults
def func(a, b, c, config=None):
    if config:
        a = config.a
        b = config.b
        c = config.c
    # ... rest unchanged

# Step 2: Update all callers to pass config
# Step 3: Make config required
def func(config: Config):
    # ... use config.a, config.b, config.c

# Step 4: Remove old parameters
```

### Database Migration (Incremental)
```python
# Add column, migrate data, switch, remove old

# Migration 1: Add new column (nullable)
ALTER TABLE users ADD COLUMN email_normalized VARCHAR(255);

# Migration 2: Backfill (batch, with progress)
UPDATE users SET email_normalized = LOWER(email) WHERE email_normalized IS NULL;

# Migration 3: Add index, make not null
CREATE INDEX idx_users_email_norm ON users(email_normalized);
ALTER TABLE users ALTER COLUMN email_normalized SET NOT NULL;

# Migration 4: Switch application to new column
# (Deploy code that reads/writes email_normalized)

# Migration 5: Drop old column (after verification)
ALTER TABLE users DROP COLUMN email;
```

---

## Decision Rules

| Refactor Size | Increments |
|---------------|------------|
| Single function | 1-3 commits |
| Class extraction | 3-10 commits |
| Module restructure | 10-30 commits |
| Architecture change | 30+ commits (feature flags) |

---

## Preferred Patterns

```python
# Commit message template
# refactor: extract validation from process_order
# 
# Extracted validate_order() function from process_order()
# to improve readability and testability.
# No behavior change.

# Git workflow
git checkout -b refactor/extract-validation
# ... make change ...
git add -p  # Stage hunks selectively
git commit -m "refactor: extract validation from process_order"
# ... run tests ...
# ... next increment ...
```

---

## Avoid

- "Refactor everything in one PR"
- Commits that break tests
- Mixing refactor + feature + bugfix
- No feature flag for risky changes
- Deleting old code before new is verified

---

## Validation Considerations

- `git log --oneline` shows clear incremental steps
- Each commit: `pytest` passes
- Bisect works (each commit builds)
- Code review per commit or small PR

---

## Related Skills

- `refactoring/safe_refactoring.md`
- `refactoring/behavior_preservation.md`
- `testing/regression_tests.md`