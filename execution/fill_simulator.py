"""Limit-order fill simulator (zero-dep, stdlib)."""

def simulate_fill(order, bar, queue_position=0):
    """Simulate a limit order fill against an OHLC bar.

    order: dict with side ('buy'/'sell'), qty, price (limit).
    bar: dict with high/low/close (and optionally volume).
    queue_position: 0 = front of queue (filled first).

    Returns dict: {filled: bool, fill_price, fill_qty, reason}.
    """
    side = str(order.get("side", "")).lower()
    qty = float(order.get("qty", 0))
    limit = float(order.get("price", 0))
    high = float(bar.get("h", bar.get("high", 0)))
    low = float(bar.get("l", bar.get("low", 0)))
    close = float(bar.get("c", bar.get("close", 0)))

    if side == "buy":
        # buy limit fills if low <= limit
        if low <= limit <= high or low <= limit:
            # queue: if queue_position > 0, may not fill on touch
            if queue_position > 0 and low > limit:
                return {"filled": False, "fill_price": None, "fill_qty": 0, "reason": "queue-not-reached"}
            fill_price = min(limit, close) if close <= limit else limit
            # tiebreak: if touched exactly, fill at limit
            fill_price = limit
            return {"filled": True, "fill_price": fill_price, "fill_qty": qty, "reason": "filled"}
        return {"filled": False, "fill_price": None, "fill_qty": 0, "reason": "not-touched"}
    elif side == "sell":
        if high >= limit:
            if queue_position > 0 and high < limit:
                return {"filled": False, "fill_price": None, "fill_qty": 0, "reason": "queue-not-reached"}
            return {"filled": True, "fill_price": limit, "fill_qty": qty, "reason": "filled"}
        return {"filled": False, "fill_price": None, "fill_qty": 0, "reason": "not-touched"}
    return {"filled": False, "fill_price": None, "fill_qty": 0, "reason": "unknown-side"}