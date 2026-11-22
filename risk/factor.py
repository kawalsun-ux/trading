"""Factor exposure helpers (zero-dep, stdlib OLS)."""


def _ols_beta(y, x):
    n = len(y)
    if n == 0 or n != len(x):
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den = sum((xi - mx) ** 2 for xi in x)
    if den <= 0:
        return 0.0
    return num / den


def factor_exposure(returns, factor_returns):
    """OLS beta of strategy returns on a single factor. Returns float."""
    return _ols_beta(returns or [], factor_returns or [])


def multi_factor_exposure(returns, factors):
    """Multi-factor OLS. factors: dict name->list. Returns dict name->beta.

    Uses successive residualization (Gram-Schmidt-ish) for simplicity.
    """
    y = [float(v) for v in (returns or [])]
    out = {}
    residual = list(y)
    for name, series in (factors or {}).items():
        x = [float(v) for v in series]
        # regress residual on x (with intercept via demeaning)
        beta = _ols_beta(residual, x)
        out[name] = beta
        # residualize
        mx = sum(x) / len(x) if x else 0.0
        my = sum(residual) / len(residual) if residual else 0.0
        residual = [r - beta * (xi - mx) for r, xi in zip(residual, x)]
    return out


def rolling_factor_exposure(returns, factor_returns, window=60):
    out = []
    for i in range(len(returns or [])):
        lo = max(0, i - window + 1)
        sl = (returns or [])[lo:i + 1]
        fl = (factor_returns or [])[lo:i + 1]
        if len(sl) < 2:
            out.append(0.0)
            continue
        out.append(_ols_beta(sl, fl))
    return out