# Stdlib: statistics

**Purpose**: Basic statistical operations on numeric data.

**When to use**: Simple statistics without NumPy/pandas dependency.

---

## Core Rules

### Measures of Central Tendency
```python
import statistics

data = [1, 2, 3, 4, 5, 6, 7, 8, 9]

statistics.mean(data)       # Arithmetic mean: 5
statistics.fmean(data)      # Fast float mean (3.8+): 5.0
statistics.median(data)     # Median: 5
statistics.median_low(data) # Low median: 5
statistics.median_high(data) # High median: 5
statistics.median_grouped(data, interval=1) # Grouped median
statistics.mode(data)       # Single mode (raises if multimodal)
statistics.multimode(data)  # List of modes (3.8+)
statistics.harmonic_mean(data)  # Harmonic mean
statistics.geometric_mean(data) # Geometric mean (3.8+)
```

### Measures of Spread
```python
statistics.stdev(data)      # Sample standard deviation
statistics.pstdev(data)     # Population standard deviation
statistics.variance(data)   # Sample variance
statistics.pvariance(data)  # Population variance
```

### Requirements
- Input: iterable of numeric (int, float, Decimal, Fraction)
- At least 2 data points for stdev/variance
- At least 1 for mean/median
- Raises `StatisticsError` for insufficient data

---

## Decision Rules

| Need | Function |
|------|----------|
| Average | `mean` / `fmean` |
| Middle value | `median` |
| Most common | `mode` / `multimode` |
| Spread (sample) | `stdev` / `variance` |
| Spread (population) | `pstdev` / `pvariance` |
| Weighted average | Manual or NumPy |

---

## Preferred Patterns

```python
def summarize(values: list[float]) -> dict:
    if not values:
        return {"count": 0}
    if len(values) == 1:
        return {"count": 1, "mean": values[0], "median": values[0]}
    
    return {
        "count": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "stdev": statistics.stdev(values),
        "min": min(values),
        "max": max(values),
    }

# Streaming (large data) — use running calculation
def running_stats():
    n = 0
    mean = 0.0
    m2 = 0.0  # Sum of squares of differences
    for x in data_stream:
        n += 1
        delta = x - mean
        mean += delta / n
        m2 += delta * (x - mean)
        if n > 1:
            yield {"mean": mean, "stdev": (m2 / (n - 1)) ** 0.5}
```

---

## Avoid

- Using for large datasets (use NumPy/pandas)
- Calling on empty iterables (raises)
- Expecting weighted statistics (not supported)
- Using `mode` on multimodal data (raises; use `multimode`)

---

## Validation Considerations

- Test with edge cases: empty, single element, two elements
- Verify numeric precision for large values
- Compare with NumPy for correctness if available

---

## Related Skills

- `generation/type_hints.md`
- `engineering/dependency_management.md` (when to add NumPy)