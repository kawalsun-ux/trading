import math
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


def entropy_pooling_weights(base_returns, view_mean, n_iter=50):
    """Exponential tilting (Esscher) to match a view on the mean.

    Returns list of weights (sum ~1) over base_returns such that the
    weighted mean approximates view_mean. Simplified entropy pooling.
    """
    rs = [float(x) for x in (base_returns or [])]
    if not rs:
        return []
    n = len(rs)
    # find theta such that sum w_i * r_i = view_mean, w_i ~ exp(theta*r_i)/Z
    theta = 0.0
    step = 1.0
    for _ in range(n_iter):
        # compute weighted mean for current theta
        ws = [math.exp(theta * r) for r in rs]
        z = sum(ws)
        wn = [w / z for w in ws]
        wmean = sum(w * r for w, r in zip(wn, rs))
        grad = wmean - float(view_mean)
        theta -= step * grad
        step *= 0.95
    ws = [math.exp(theta * r) for r in rs]
    z = sum(ws)
    return [w / z for w in ws]
