"""Mean-reversion / OU helpers (zero-dep, stdlib)."""

import math


def mean_reversion_speed(series):
    """OU speed kappa per step from OLS of dy on lagged level."""
    s = [float(x) for x in (series or [])]
    n = len(s)
    if n < 3:
        return 0.0
    # dy_t = s[t]-s[t-1]; lagged = s[t-1]
    xs = [s[i - 1] for i in range(1, n)]
    ys = [s[i] - s[i - 1] for i in range(1, n)]
    nn = len(xs)
    mx = sum(xs) / nn
    my = sum(ys) / nn
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den <= 0:
        return 0.0
    slope = num / den
    return -slope


def half_life(series):
    kappa = mean_reversion_speed(series)
    if kappa <= 0:
        return float("inf")
    return math.log(2.0) / kappa


def zscore_latest(series):
    s = [float(x) for x in (series or [])]
    if not s:
        return 0.0
    m = sum(s) / len(s)
    var = sum((x - m) ** 2 for x in s) / len(s)
    sd = math.sqrt(var) if var > 0 else 0.0
    if sd <= 0:
        return 0.0
    return (s[-1] - m) / sd