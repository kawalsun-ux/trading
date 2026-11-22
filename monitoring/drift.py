"""Drift detection helpers (zero-dep, stdlib)."""

import math


def psi(expected, actual, buckets=10):
    """Population Stability Index between two distributions."""
    if not expected or not actual:
        return 0.0
    combined = sorted(list(expected) + list(actual))
    n = len(combined)
    cuts = []
    for i in range(1, buckets):
        idx = min(n - 1, int(i * n / buckets))
        cuts.append(combined[idx])
    def bucketize(vals):
        counts = [0] * buckets
        for v in vals:
            placed = False
            for b in range(buckets - 1):
                if v <= cuts[b]:
                    counts[b] += 1
                    placed = True
                    break
            if not placed:
                counts[buckets - 1] += 1
        total = sum(counts) or 1
        return [c / total for c in counts]
    pe = bucketize(expected)
    pa = bucketize(actual)
    eps = 1e-6
    psi_val = 0.0
    for a, b in zip(pe, pa):
        a = max(a, eps)
        b = max(b, eps)
        psi_val += (b - a) * math.log(b / a)
    return psi_val


def ks_statistic(a, b):
    """Two-sample KS statistic (max CDF difference)."""
    if not a or not b:
        return 0.0
    sa = sorted(a)
    sb = sorted(b)
    all_vals = sorted(set(sa + sb))
    def cdf(vals, x):
        return sum(1 for v in vals if v <= x) / len(vals)
    d = 0.0
    for x in all_vals:
        d = max(d, abs(cdf(sa, x) - cdf(sb, x)))
    return d


def rolling_mean(series, window=20):
    out = []
    for i in range(len(series or [])):
        lo = max(0, i - window + 1)
        sl = (series or [])[lo:i + 1]
        out.append(sum(sl) / len(sl) if sl else 0.0)
    return out