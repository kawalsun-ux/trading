"""Drawdown / path-risk helpers (zero-dep, stdlib)."""


def max_drawdown(equity):
    if not equity:
        return 0.0
    peak = equity[0]
    mdd = 0.0
    for x in equity:
        if x > peak:
            peak = x
        dd = (peak - x) / peak if peak > 0 else 0.0
        if dd > mdd:
            mdd = dd
    return mdd


def drawdown_series(equity):
    out = []
    peak = None
    for x in equity or []:
        if peak is None or x > peak:
            peak = x
        dd = (peak - x) / peak if peak and peak > 0 else 0.0
        out.append(dd)
    return out


def max_drawdown_duration(equity):
    if not equity:
        return 0
    peak = equity[0]
    peak_idx = 0
    dur = 0
    maxdur = 0
    for i, x in enumerate(equity):
        if x >= peak:
            peak = x
            peak_idx = i
            dur = 0
        else:
            dur = i - peak_idx
            if dur > maxdur:
                maxdur = dur
    return maxdur


def time_to_recovery(equity):
    """Bars from max-drawdown trough back to a new peak (or -1)."""
    if not equity:
        return -1
    # find trough index of max drawdown
    peak = equity[0]
    peak_idx = 0
    mdd = 0.0
    trough_idx = 0
    for i, x in enumerate(equity):
        if x > peak:
            peak = x
            peak_idx = i
        dd = (peak - x) / peak if peak > 0 else 0.0
        if dd > mdd:
            mdd = dd
            trough_idx = i
    for j in range(trough_idx + 1, len(equity)):
        if equity[j] >= peak:
            return j - trough_idx
    return -1


def ulcer_index(equity):
    ds = drawdown_series(equity)
    if not ds:
        return 0.0
    return (sum(d * d for d in ds) / len(ds)) ** 0.5