"""Narrow baseline checkpoint helpers (zero-dep)."""


def baseline_checkpoint(metrics):
    """Sanity checks before expanding search. Returns (ok, issues)."""
    issues = []
    m = metrics or {}
    if m.get("trades", 0) < 5:
        issues.append("too-few-trades")
    if m.get("maxDD", 0) > 0.5:
        issues.append("excessive-drawdown")
    if m.get("win_rate", 0) == 0 and m.get("trades", 0) > 0:
        issues.append("zero-win-rate")
    return len(issues) == 0, issues