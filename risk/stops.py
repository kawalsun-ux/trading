"""Composable stop-loss helpers (zero-dep, stdlib)."""


def trailing_stop(prices, trail_pct):
    """Trailing stop level series. Returns list of stop levels."""
    if not prices:
        return []
    stops = []
    peak = prices[0]
    for p in prices:
        if p > peak:
            peak = p
        stops.append(peak * (1 - trail_pct))
    return stops


def atr_stop(prices, atr_values, multiplier=2.0, side="long"):
    """ATR-based stop level. side: 'long' or 'short'."""
    out = []
    for p, a in zip(prices or [], atr_values or []):
        if side == "long":
            out.append(p - multiplier * a)
        else:
            out.append(p + multiplier * a)
    return out


def chandelier_stop(prices, atr_values, multiplier=3.0, lookback=22):
    """Chandelier exit: highest high - multiplier*ATR (long)."""
    out = []
    for i, p in enumerate(prices or []):
        window = (prices or [])[max(0, i - lookback + 1):i + 1]
        hh = max(window) if window else p
        a = atr_values[i] if i < len(atr_values or []) else 0.0
        out.append(hh - multiplier * a)
    return out


def time_stop(entry_idx, current_idx, max_bars):
    """True if position held longer than max_bars."""
    return (current_idx - entry_idx) >= max_bars