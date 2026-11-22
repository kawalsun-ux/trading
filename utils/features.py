"""Feature engineering helpers (zero-dep, stdlib)."""

import math


def _f(x, default=0.0):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    if v != v or v in (float("inf"), float("-inf")):
        return default
    return v


def zscore(series, lookback=20):
    """Trailing z-score. Returns list same length; warmup -> 0.0."""
    vals = [_f(v) for v in (series or [])]
    n = len(vals)
    out = [0.0] * n
    if n == 0:
        return out
    lookback = max(1, int(lookback or 20))
    for i in range(n):
        win = vals[max(0, i - lookback + 1): i + 1]
        m = sum(win) / len(win)
        var = sum((x - m) ** 2 for x in win) / len(win)
        sd = math.sqrt(var) if var > 0 else 0.0
        out[i] = (vals[i] - m) / sd if sd > 0 else 0.0
    return out


def rolling_vol(series, lookback=20, annualize=False):
    """Rolling standard deviation."""
    vals = [_f(v) for v in (series or [])]
    n = len(vals)
    out = [0.0] * n
    lookback = max(1, int(lookback or 20))
    for i in range(n):
        win = vals[max(0, i - lookback + 1): i + 1]
        m = sum(win) / len(win)
        var = sum((x - m) ** 2 for x in win) / len(win)
        sd = math.sqrt(var) if var > 0 else 0.0
        if annualize:
            sd *= math.sqrt(252.0)
        out[i] = sd
    return out


def momentum(series, lookback=20):
    """Simple momentum: price change over lookback."""
    vals = [_f(v) for v in (series or [])]
    n = len(vals)
    out = [0.0] * n
    lb = max(1, int(lookback or 20))
    for i in range(lb, n):
        if vals[i - lb] != 0:
            out[i] = vals[i] / vals[i - lb] - 1.0
    return out


def reversal(series, lookback=5):
    """Short-term reversal: negative of short-horizon return."""
    m = momentum(series, lookback=lookback)
    return [-x for x in m]


def liquidity_proxy(highs, lows, closes, volumes):
    """Amihud-style illiquidity: |return| / dollar volume."""
    hs = [_f(x) for x in (highs or [])]
    ls = [_f(x) for x in (lows or [])]
    cs = [_f(x) for x in (closes or [])]
    vs = [_f(x) for x in (volumes or [])]
    n = min(len(hs), len(ls), len(cs), len(vs))
    out = [0.0] * n
    for i in range(1, n):
        if cs[i - 1] > 0 and vs[i] > 0 and cs[i] > 0:
            ret = abs(cs[i] / cs[i - 1] - 1.0)
            dv = cs[i] * vs[i]
            if dv > 0:
                out[i] = ret / dv
    return out


def point_in_time_align(series, release_dates):
    """Align a slow-moving series to release dates (no lookahead).

    series: list of values (one per release).
    release_dates: list of bar indices when each value becomes available.
    Returns a list aligned to bar index (length = max(release_dates)+1 or len(series)).
    """
    if not series or not release_dates:
        return list(series or [])
    n = len(series)
    rd = list(release_dates)
    # pad
    while len(rd) < n:
        rd.append(rd[-1] if rd else 0)
    max_idx = max(rd) if rd else 0
    out = [None] * (max_idx + 1)
    # fill forward
    cur = None
    cur_i = 0
    # build release map
    releases = sorted(zip(rd, series), key=lambda t: t[0])
    ri = 0
    for i in range(max_idx + 1):
        while ri < len(releases) and releases[ri][0] <= i:
            cur = releases[ri][1]
            ri += 1
        out[i] = cur
    return out


def calendar_encoding(ts, period=365.25):
    """Cyclical sin/cos encoding of a timestamp's day-of-year."""
    try:
        t = float(ts)
    except (TypeError, ValueError):
        return (0.0, 0.0)
    # day of year approx
    day = (t / 86400.0) % period
    ang = 2.0 * math.pi * day / period
    return (math.sin(ang), math.cos(ang))


def feature_spec(name, horizon=None, driver=None, role=None):
    """Document a feature specification as a dict."""
    return {
        "name": name,
        "horizon": horizon,
        "driver": driver,
        "role": role,  # 'signal' | 'state' | 'conditioning'
    }