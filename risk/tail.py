"""Tail risk helpers (zero-dep, stdlib)."""

import math


def _returns(returns):
    return [float(x) for x in (returns or [])]


def var_historical(returns, alpha=0.05):
    rs = sorted(_returns(returns))
    if not rs:
        return 0.0
    idx = max(0, min(len(rs) - 1, int(alpha * len(rs))))
    return -rs[idx]


def var_parametric(returns, alpha=0.05):
    rs = _returns(returns)
    if len(rs) < 2:
        return 0.0
    m = sum(rs) / len(rs)
    var = sum((x - m) ** 2 for x in rs) / len(rs)
    sd = math.sqrt(var)
    # normal quantile approx (z for alpha)
    # use simple inverse via error function not available; use common z values
    z = {0.01: 2.326, 0.05: 1.645, 0.10: 1.282}.get(alpha, 1.645)
    return -(m - z * sd)


def var_cornish_fisher(returns, alpha=0.05):
    rs = _returns(returns)
    if len(rs) < 3:
        return var_parametric(rs, alpha)
    m = sum(rs) / len(rs)
    var = sum((x - m) ** 2 for x in rs) / len(rs)
    sd = math.sqrt(var) if var > 0 else 0.0
    if sd <= 0:
        return 0.0
    skew = sum((x - m) ** 3 for x in rs) / (len(rs) * sd ** 3)
    kurt = sum((x - m) ** 4 for x in rs) / (len(rs) * sd ** 4) - 3.0
    z = {0.01: 2.326, 0.05: 1.645, 0.10: 1.282}.get(alpha, 1.645)
    z_cf = (z + (z ** 2 - 1) * skew / 6.0
            + (z ** 3 - 3 * z) * kurt / 24.0
            - (2 * z ** 3 - 5 * z) * (skew ** 2) / 36.0)
    return -(m - z_cf * sd)


def cvar(returns, alpha=0.05):
    rs = sorted(_returns(returns))
    if not rs:
        return 0.0
    k = max(1, int(alpha * len(rs)))
    tail = rs[:k]
    return -sum(tail) / len(tail)


def var_backtest(violations, n, alpha=0.05):
    """Kupiec POF test. Returns (statistic, p_value_approx)."""
    v = int(violations)
    if n <= 0 or v < 0 or v > n:
        return 0.0, 1.0
    p = alpha
    # likelihood ratio
    if v == 0:
        lr = -2.0 * (n * math.log(1 - p))
    elif v == n:
        lr = -2.0 * (n * math.log(p))
    else:
        lr = -2.0 * ((n - v) * math.log((1 - p) / (1 - v / n)) + v * math.log(p / (v / n)))
    # chi-square 1 df p-value approx via survival; use simple threshold
    # p-value approximated by exp(-lr/2) (rough) clamped
    pval = math.exp(-lr / 2.0)
    if pval > 1.0:
        pval = 1.0
    return lr, pval