"""Live safety / preflight helpers (zero-dep, stdlib)."""


def preflight_checks(account, positions, max_exposure):
    """Return list of issues (empty = ok)."""
    issues = []
    try:
        if float(account.get("cash", 0)) < 0:
            issues.append("negative-cash")
    except (TypeError, ValueError, AttributeError):
        issues.append("bad-account")
    total = sum(abs(float(p.get("qty", 0))) for p in (positions or []))
    if total > max_exposure:
        issues.append("exposure-exceeded")
    return issues


def shadow_mode(backtest_fill, live_fill):
    """Log divergence between backtest and live fills."""
    if backtest_fill is None or live_fill is None:
        return {"diverged": True, "reason": "missing-fill"}
    if backtest_fill != live_fill:
        return {"diverged": True, "backtest": backtest_fill, "live": live_fill}
    return {"diverged": False}