"""Backtest-vs-live parity checks (zero-dep, stdlib)."""


def verify_parity(backtest_signals, live_signals):
    """Compare two lists of signal dicts. Returns mismatch report."""
    mismatches = []
    n = max(len(backtest_signals or []), len(live_signals or []))
    for i in range(n):
        bs = (backtest_signals or [])[i] if i < len(backtest_signals or []) else None
        ls = (live_signals or [])[i] if i < len(live_signals or []) else None
        if bs != ls:
            mismatches.append({"index": i, "backtest": bs, "live": ls})
    return {"ok": len(mismatches) == 0, "mismatches": mismatches, "count": len(mismatches)}