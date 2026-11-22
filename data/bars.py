"""Bar aggregation helpers (zero-dep, stdlib)."""

import math


def time_bars(candles, n=1):
    """Pass-through; time bars are the input. Returns list copy."""
    return list(candles or [])


def volume_bars(ticks, threshold):
    """Aggregate ticks into bars when cumulative volume >= threshold."""
    out = []
    cur = {"o": None, "h": None, "l": None, "c": None, "v": 0.0, "ts": None, "n": 0}
    for t in (ticks or []):
        price = float(t.get("price", t.get("c", t.get("close", 0))))
        vol = float(t.get("volume", t.get("v", 1)))
        ts = t.get("ts", t.get("time"))
        if cur["o"] is None:
            cur["o"] = cur["h"] = cur["l"] = cur["c"] = price
            cur["ts"] = ts
        cur["h"] = max(cur["h"], price)
        cur["l"] = min(cur["l"], price)
        cur["c"] = price
        cur["v"] += vol
        cur["n"] += 1
        if cur["v"] >= threshold:
            out.append({k: cur[k] for k in ("o", "h", "l", "c", "v", "ts", "n")})
            cur = {"o": None, "h": None, "l": None, "c": None, "v": 0.0, "ts": None, "n": 0}
    if cur["o"] is not None and cur["n"] > 0:
        out.append({k: cur[k] for k in ("o", "h", "l", "c", "v", "ts", "n")})
    return out


def dollar_bars(ticks, threshold):
    """Aggregate ticks into bars when cumulative $ volume >= threshold."""
    out = []
    cur = {"o": None, "h": None, "l": None, "c": None, "v": 0.0, "dollar": 0.0, "ts": None, "n": 0}
    for t in (ticks or []):
        price = float(t.get("price", t.get("c", t.get("close", 0))))
        vol = float(t.get("volume", t.get("v", 1)))
        ts = t.get("ts", t.get("time"))
        if cur["o"] is None:
            cur["o"] = cur["h"] = cur["l"] = cur["c"] = price
            cur["ts"] = ts
        cur["h"] = max(cur["h"], price)
        cur["l"] = min(cur["l"], price)
        cur["c"] = price
        cur["v"] += vol
        cur["dollar"] += price * vol
        cur["n"] += 1
        if cur["dollar"] >= threshold:
            out.append({k: cur[k] for k in ("o", "h", "l", "c", "v", "ts", "n", "dollar")})
            cur = {"o": None, "h": None, "l": None, "c": None, "v": 0.0, "dollar": 0.0, "ts": None, "n": 0}
    if cur["o"] is not None and cur["n"] > 0:
        out.append({k: cur[k] for k in ("o", "h", "l", "c", "v", "ts", "n", "dollar")})
    return out


def tick_bars(ticks, n):
    """Aggregate every `n` ticks into a bar."""
    n = max(1, int(n or 1))
    out = []
    cur = {"o": None, "h": None, "l": None, "c": None, "v": 0.0, "ts": None, "count": 0}
    for t in (ticks or []):
        price = float(t.get("price", t.get("c", t.get("close", 0))))
        vol = float(t.get("volume", t.get("v", 1)))
        ts = t.get("ts", t.get("time"))
        if cur["o"] is None:
            cur["o"] = cur["h"] = cur["l"] = cur["c"] = price
            cur["ts"] = ts
        cur["h"] = max(cur["h"], price)
        cur["l"] = min(cur["l"], price)
        cur["c"] = price
        cur["v"] += vol
        cur["count"] += 1
        if cur["count"] >= n:
            out.append({k: cur[k] for k in ("o", "h", "l", "c", "v", "ts", "count")})
            cur = {"o": None, "h": None, "l": None, "c": None, "v": 0.0, "ts": None, "count": 0}
    if cur["o"] is not None and cur["count"] > 0:
        out.append({k: cur[k] for k in ("o", "h", "l", "c", "v", "ts", "count")})
    return out


def sessionize(candles, session_min=1440):
    """Tag each candle with a session index based on ts."""
    out = []
    width = max(1, int(session_min or 1440)) * 60
    cur = None
    idx = -1
    for c in (candles or []):
        row = dict(c)
        ts = c.get("ts", c.get("time")) if isinstance(c, dict) else None
        try:
            t = float(ts)
            s = int(t // width)
        except (TypeError, ValueError):
            s = cur if cur is not None else 0
        if s != cur:
            cur = s
            idx += 1
        row["session"] = idx
        out.append(row)
    return out