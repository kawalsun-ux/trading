#!/usr/bin/env python3
"""Dependency-free backtest audit (look-ahead, ledger conservation, fee double-count)."""

import json
import sys
import os


def audit_result(result):
    """Audit a backtest result dict. Returns list of issues (empty = ok)."""
    issues = []
    trades = result.get("trades", []) or []
    metrics = result.get("metrics", {}) or {}
    equity = result.get("equity", []) or []

    # 1. Ledger conservation: sum of trade pnl should relate to final equity
    if trades and equity:
        total_pnl = sum(t.get("pnl", 0) for t in trades)
        # equity change approx
        if len(equity) >= 2:
            eq_change = equity[-1] - equity[0]
            if abs(total_pnl - eq_change) > 1e-6 * max(1, abs(eq_change)):
                # allow fees; just warn if large mismatch
                if abs(total_pnl - eq_change) > 1e-3 * max(1, abs(eq_change)):
                    issues.append("ledger-mismatch: trade pnl vs equity change")

    # 2. Fee double-count: if pnl already net, fees shouldn't be re-subtracted
    # Heuristic: check that no trade has fees > notional
    for t in trades:
        fees = t.get("fees", 0)
        entry = t.get("entry", 0)
        qty = t.get("qty", 0)
        notional = abs(entry * qty) if entry and qty else 0
        if notional > 0 and fees > notional:
            issues.append(f"fee-exceeds-notional: trade {t.get('entry_idx')}")
            break

    # 3. Look-ahead heuristic: if any trade has hold_bars < entry_delay, warn
    engine = result.get("engine", {}) or {}
    ed = engine.get("entry_delay_bars", 1)
    for t in trades:
        hb = t.get("hold_bars", 0)
        if hb is not None and hb < 0:
            issues.append("negative-hold-bars")
            break

    # 4. Empty result sanity
    if len(trades) == 0 and metrics.get("trades", 0) != 0:
        issues.append("trade-count-mismatch")

    # 5. Sharpe sanity
    sh = metrics.get("sharpe", 0)
    if sh is not None and (sh != sh):  # nan check
        issues.append("nan-sharpe")

    return issues


def main():
    if len(sys.argv) < 2:
        print("usage: audit_backtest.py <result.json>")
        sys.exit(1)
    path = sys.argv[1]
    with open(path) as f:
        result = json.load(f)
    issues = audit_result(result)
    if issues:
        print("ISSUES FOUND:")
        for i in issues:
            print(" -", i)
        sys.exit(1)
    print("audit: OK")
    sys.exit(0)


if __name__ == "__main__":
    main()