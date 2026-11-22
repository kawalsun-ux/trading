"""Realized volatility and related estimators (zero-dep, stdlib)."""

import math


def realized_variance(returns):
    return sum(r * r for r in (returns or []))


def realized_volatility(returns):
    return math.sqrt(realized_variance(returns or []))


def annualized_volatility(returns, periods_per_year):
    n = len(returns or [])
    if n == 0:
        return 0.0
    return math.sqrt((realized_variance(returns) / n) * periods_per_year)


def realized_skewness(returns):
    n = len(returns or [])
    if n == 0:
        return 0.0
    s2 = sum(r * r for r in returns)
    s3 = sum(r * r * r for r in returns)
    if s2 == 0:
        return 0.0
    return math.sqrt(n) * s3 / (s2 ** 1.5)


def realized_kurtosis(returns):
    n = len(returns or [])
    if n == 0:
        return 0.0
    s2 = sum(r * r for r in returns)
    s4 = sum(r ** 4 for r in returns)
    if s2 == 0:
        return 0.0
    return n * s4 / (s2 * s2)


# --- range-based volatility (from OHLC candles) ---

def _candle_fields(bars):
    out = []
    for b in (bars or []):
        if isinstance(b, dict):
            o = float(b.get("o", b.get("open", 0)))
            h = float(b.get("h", b.get("high", 0)))
            l = float(b.get("l", b.get("low", 0)))
            c = float(b.get("c", b.get("close", 0)))
        else:
            o, h, l, c = (float(x) for x in b)
        out.append((o, h, l, c))
    return out


def parkinson_volatility(bars):
    """Parkinson (1980) high-low volatility per bar."""
    cs = _candle_fields(bars)
    n = len(cs)
    if n == 0:
        return 0.0
    s = sum((math.log(h / l)) ** 2 for (o, h, l, c) in cs if h > 0 and l > 0)
    return math.sqrt(s / (4.0 * math.log(2.0) * n))


def garman_klass_volatility(bars):
    """Garman-Klass (1980) OHLC volatility per bar."""
    cs = _candle_fields(bars)
    n = len(cs)
    if n == 0:
        return 0.0
    s = 0.0
    for (o, h, l, c) in cs:
        if o > 0 and h > 0 and l > 0 and c > 0:
            s += 0.5 * (math.log(h / l)) ** 2 - (2 * math.log(2) - 1) * (math.log(c / o)) ** 2
    return math.sqrt(s / n)


def rogers_satchell_volatility(bars):
    """Rogers-Satchell (1991) drift-independent volatility per bar."""
    cs = _candle_fields(bars)
    n = len(cs)
    if n == 0:
        return 0.0
    s = 0.0
    for (o, h, l, c) in cs:
        if o > 0 and h > 0 and l > 0 and c > 0:
            s += math.log(h / c) * math.log(h / o) + math.log(l / c) * math.log(l / o)
    return math.sqrt(s / n) if s >= 0 else 0.0


def yang_zhang_volatility(bars):
    """Yang-Zhang (2000) drift-independent, jump-robust volatility per bar."""
    cs = _candle_fields(bars)
    n = len(cs)
    if n < 2:
        return 0.0
    # overnight returns
    oc = [math.log(cs[i][3] / cs[i - 1][0]) for i in range(1, n) if cs[i - 1][0] > 0 and cs[i][3] > 0]
    # open-to-close
    co = [math.log(cs[i][3] / cs[i][0]) for i in range(n) if cs[i][0] > 0 and cs[i][3] > 0]
    if not oc or not co:
        return 0.0
    # k
    n1 = len(oc)
    vo = sum((r - sum(oc) / n1) ** 2 for r in oc) / (n1 - 1) if n1 > 1 else 0.0
    vc = sum((r - sum(co) / len(co)) ** 2 for r in co) / (len(co) - 1) if len(co) > 1 else 0.0
    # rs variance
    rs = 0.0
    for (o, h, l, c) in cs:
        if o > 0 and h > 0 and l > 0 and c > 0:
            rs += (math.log(h / c) * math.log(h / o) + math.log(l / c) * math.log(l / o))
    rs = rs / n
    k = 0.34 / (1.34 + (n + 1) / (n - 1))
    var = vo + k * vc + (1 - k) * rs
    return math.sqrt(var) if var > 0 else 0.0


# --- jump-robust variance (bipower, MinRV, MedRV) ---

def bipower_variation(returns):
    n = len(returns or [])
    if n < 2:
        return 0.0
    s = sum(abs(returns[i - 1]) * abs(returns[i]) for i in range(1, n))
    return (math.pi / 2.0) * s


def jump_variation(returns):
    rv = realized_variance(returns)
    bv = bipower_variation(returns)
    return max(rv - bv, 0.0)


def relative_jump(returns):
    rv = realized_variance(returns)
    if rv <= 0:
        return 0.0
    return jump_variation(returns) / rv


def min_rv(returns):
    n = len(returns or [])
    if n < 2:
        return 0.0
    s = 0.0
    for i in range(1, n):
        m = min(abs(returns[i - 1]), abs(returns[i]))
        s += m * m
    scale = math.pi / (math.pi - 2.0)
    return scale * (n / (n - 1)) * s


def med_rv(returns):
    n = len(returns or [])
    if n < 3:
        return 0.0
    s = 0.0
    for i in range(1, n - 1):
        a = abs(returns[i - 1]); b = abs(returns[i]); c = abs(returns[i + 1])
        med = sorted([a, b, c])[1]
        s += med * med
    scale = math.pi / (6.0 - 4.0 * math.sqrt(3.0) + math.pi)
    return scale * (n / (n - 2.0)) * s


def realized_quarticity(returns):
    n = len(returns or [])
    if n == 0:
        return 0.0
    return (n / 3.0) * sum(r ** 4 for r in returns)


# --- HAR-RV forecast ---

def har_forecast(rv_series, daily=1, weekly=5, monthly=22):
    """One-step-ahead HAR-RV forecast. Returns (forecast, (b0, bd, bw, bm))."""
    s = [float(x) for x in (rv_series or [])]
    n = len(s)
    if n < monthly + 2:
        return 0.0, (0.0, 0.0, 0.0, 0.0)
    # build regression: y_t = b0 + bd*RV_{t-1}^(d) + bw*RV_{t-1}^(w) + bm*RV_{t-1}^(m)
    # solve via least squares (Gaussian elimination, 4x4)
    rows = []
    ys = []
    for t in range(monthly, n):
        rd = s[t - 1]
        rw = sum(s[t - weekly:t]) / weekly if t >= weekly else s[t - 1]
        rm = sum(s[t - monthly:t]) / monthly if t >= monthly else s[t - 1]
        rows.append([1.0, rd, rw, rm])
        ys.append(s[t])
    # solve normal equations A^T A beta = A^T y
    k = 4
    AtA = [[0.0] * k for _ in range(k)]
    Aty = [0.0] * k
    for row, y in zip(rows, ys):
        for i in range(k):
            Aty[i] += row[i] * y
            for j in range(k):
                AtA[i][j] += row[i] * row[j]
    # gaussian elimination
    # augment
    M = [row[:] + [Aty[i]] for i, row in enumerate(AtA)]
    for col in range(k):
        # pivot
        piv = max(range(col, k), key=lambda r: abs(M[r][col]))
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        if abs(pv) < 1e-12:
            return 0.0, (0.0, 0.0, 0.0, 0.0)
        for j in range(col, k + 1):
            M[col][j] /= pv
        for r in range(k):
            if r == col:
                continue
            factor = M[r][col]
            for j in range(col, k + 1):
                M[r][j] -= factor * M[col][j]
    beta = [M[i][k] for i in range(k)]
    # forecast
    last = s[-1]
    rw = sum(s[-weekly:]) / weekly
    rm = sum(s[-monthly:]) / monthly
    fc = beta[0] + beta[1] * last + beta[2] * rw + beta[3] * rm
    return fc, (beta[0], beta[1], beta[2], beta[3])