# Stdlib: datetime

**Purpose**: Date and time handling with timezone awareness.

**When to use**: All date/time operations. Avoid `time` module for new code.

---

## Core Rules

### Key Types
```python
from datetime import datetime, date, time, timedelta, timezone, tzinfo

# date: year, month, day (no time, no tz)
# time: hour, minute, second, microsecond, tzinfo
# datetime: date + time + tzinfo
# timedelta: duration
# timezone: fixed offset tzinfo
# ZoneInfo (Python 3.9+): IANA timezone database
```

### Creation
```python
# date
date(2024, 1, 15)
date.fromisoformat("2024-01-15")
date.today()

# time
time(14, 30, 0)
time.fromisoformat("14:30:00")

# datetime (naive = no timezone)
datetime(2024, 1, 15, 14, 30, 0)
datetime.fromisoformat("2024-01-15T14:30:00")
datetime.now()          # Local naive
datetime.utcnow()       # DEPRECATED — avoid

# datetime (aware = with timezone)
datetime.now(timezone.utc)
datetime.now(ZoneInfo("America/New_York"))
datetime.fromisoformat("2024-01-15T14:30:00+00:00")
```

### Timezone Handling (Critical)
```python
from zoneinfo import ZoneInfo  # Python 3.9+

# UTC
utc = timezone.utc
dt_utc = datetime.now(utc)

# Named timezone
ny = ZoneInfo("America/New_York")
dt_ny = datetime.now(ny)

# Convert between timezones
dt_ny = dt_utc.astimezone(ny)

# Make naive aware (assume UTC)
dt_aware = dt_naive.replace(tzinfo=timezone.utc)

# Make aware naive (lose tz info)
dt_naive = dt_aware.replace(tzinfo=None)
```

### Operations
```python
# Arithmetic
dt + timedelta(days=7)
dt - timedelta(hours=3)
dt1 - dt2  # Returns timedelta

# Comparison (only aware-aware or naive-naive)
dt1 < dt2

# Replace fields
dt.replace(year=2025, hour=0)

# Formatting
dt.isoformat()           # "2024-01-15T14:30:00+00:00"
dt.strftime("%Y-%m-%d %H:%M:%S")
dt.strftime("%Y-%m-%dT%H:%M:%S%z")

# Parsing
datetime.fromisoformat("2024-01-15T14:30:00+00:00")  # Python 3.11+ handles all ISO
datetime.strptime("15/01/2024", "%d/%m/%Y")
```

### Timedelta
```python
timedelta(days=7, hours=3, minutes=30)
timedelta(weeks=1)
timedelta.total_seconds()  # Float seconds
```

---

## Decision Rules

| Situation | Type |
|-----------|------|
| Calendar date only | `date` |
| Time of day only | `time` |
| Timestamp (point in time) | `datetime` (aware!) |
| Duration | `timedelta` |
| Fixed offset | `timezone(timedelta(hours=5))` |
| Named timezone | `ZoneInfo("Region/City")` |

---

## Preferred Patterns

```python
# Always use aware datetimes for timestamps
def now_utc() -> datetime:
    return datetime.now(timezone.utc)

# Parse ISO with fallback
def parse_iso(s: str) -> datetime:
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        # Handle common variations
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%d"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        raise

# Serialize for JSON/API
def serialize_dt(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()

# Deserialize from JSON/API
def deserialize_dt(s: str) -> datetime:
    dt = parse_iso(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
```

---

## Avoid

- `datetime.utcnow()` (deprecated, returns naive)
- Naive datetimes for timestamps (ambiguous)
- `pytz` (use `zoneinfo` stdlib in 3.9+)
- String manipulation for date math
- Comparing aware to naive (raises TypeError)
- `time.mktime` / `time.gmtime` (use datetime methods)

---

## Python 3.11+ Improvements

```python
# fromisoformat handles all ISO 8601 formats
datetime.fromisoformat("2024-01-15T14:30:00+05:30")
datetime.fromisoformat("2024-01-15")  # Returns date, not datetime!

# UTC shortcut
datetime.UTC  # timezone.utc singleton
```

---

## Validation Considerations

- Always validate timezone on input
- Use `isinstance(dt, datetime)` not `type(dt) is datetime`
- `date` and `datetime` are not comparable
- `timedelta` has no months/years (variable length)

---

## Related Skills

- `stdlib/json.md` (serialization)
- `engineering/configuration.md`
- `security/input_validation.md`
- `generation/type_hints.md`