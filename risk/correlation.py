"""Correlation helpers for position/risk limits (zero-dep, stdlib)."""

import math


def _corr(a, b):
    n = min(len(a or []), len(b or []))
    if n < 2:
        return 0.0
    x = [float(v) for v in (a or [])[:n]]
    y = [float(v) for v in (b or [])[:n]]
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    dx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
    dy = math.sqrt(sum((yi - my) ** 2 for yi in y))
    if dx <= 0 or dy <= 0:
        return 0.0
    return num / (dx * dy)


def pairwise_correlations(returns_map):
    """returns_map: dict name->list of returns. Returns dict (a,b)->corr."""
    out = {}
    names = list(returns_map or {})
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            out[(names[i], names[j])] = _corr(returns_map[names[i]], returns_map[names[j]])
    return out


def correlation_limit_check(returns_map, threshold=0.7):
    """Return list of pairs exceeding threshold."""
    pairs = pairwise_correlations(returns_map)
    return [(a, b, c) for (a, b), c in pairs.items() if abs(c) > threshold]