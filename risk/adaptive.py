"""Adaptive risk controls (zero-dep, stdlib)."""


def vol_targeting(positions, realized_vol, target_vol):
    """Scale positions so realized vol matches target vol."""
    try:
        rv = float(realized_vol); tv = float(target_vol)
    except (TypeError, ValueError):
        return list(positions or [])
    if rv <= 0:
        return list(positions or [])
    scale = tv / rv
    return [float(p) * scale for p in (positions or [])]


def exposure_cap(positions, max_exposure):
    """Clip aggregate exposure to max_exposure (sum of abs positions)."""
    positions = [float(p) for p in (positions or [])]
    total = sum(abs(p) for p in positions)
    if total <= 0 or total <= max_exposure:
        return positions
    scale = max_exposure / total
    return [p * scale for p in positions]


def kill_switch(metrics, thresholds):
    """Return (triggered: bool, reason: str)."""
    m = metrics or {}
    t = thresholds or {}
    # max drawdown
    if "max_drawdown" in t and m.get("max_dd", 0) > t["max_drawdown"]:
        return True, "max-drawdown-breached"
    # sharpe floor
    if "min_sharpe" in t and m.get("sharpe", 0) < t["min_sharpe"]:
        return True, "sharpe-below-floor"
    # trade count anomaly
    if "min_trades" in t and m.get("trades", 0) < t["min_trades"]:
        return True, "too-few-trades"
    return False, "ok"