"""Stress testing helpers (zero-dep, stdlib)."""

import random


def historical_replay(returns, crisis_returns):
    """Apply a crisis return sequence to a strategy's return series.

    Returns list of stressed returns (element-wise sum).
    """
    rs = [float(x) for x in (returns or [])]
    cs = [float(x) for x in (crisis_returns or [])]
    n = min(len(rs), len(cs))
    return [rs[i] + cs[i] for i in range(n)]


def monte_carlo_stress(returns, n_paths=100, shock=-0.2, seed=None):
    """Generate stressed return paths by injecting a shock into random subsets.

    Returns list of path-level total returns.
    """
    if seed is not None:
        random.seed(seed)
    rs = [float(x) for x in (returns or [])]
    if not rs:
        return []
    out = []
    for _ in range(n_paths):
        path = list(rs)
        # inject shock into a random contiguous block
        if len(path) > 5:
            start = random.randrange(0, len(path) - 4)
            for j in range(start, min(start + 5, len(path))):
                path[j] += shock / 5.0
        total = 1.0
        for r in path:
            total *= (1.0 + r)
        out.append(total - 1.0)
    return out