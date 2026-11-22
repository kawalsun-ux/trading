"""Transaction cost analysis helpers (zero-dep, stdlib)."""


def effective_half_spread(price, mid, side):
    d = 1 if str(side).lower() == "buy" else -1
    return d * (price - mid)


def effective_spread(price, mid, side):
    return 2 * effective_half_spread(price, mid, side)


def realized_spread(price, mid_after, side):
    d = 1 if str(side).lower() == "buy" else -1
    return 2 * d * (price - mid_after)


def price_impact(price, mid, mid_after, side):
    """Permanent component: effective - realized (half-spread units)."""
    return effective_half_spread(price, mid, side) - effective_half_spread(price, mid_after, side)


def implementation_shortfall(arrival_price, exec_price, side, qty, benchmark_price=None):
    """Implementation shortfall in price units * qty."""
    d = 1 if str(side).lower() == "buy" else -1
    shortfall = d * (exec_price - arrival_price) * qty
    if benchmark_price is not None:
        shortfall += d * (arrival_price - benchmark_price) * qty
    return shortfall


def kyle_lambda_from_trades(trades):
    """Kyle's lambda from list of (price_change, signed_volume)."""
    if not trades or len(trades) < 2:
        return 0.0
    xs = [float(t[1]) for t in trades]
    ys = [float(t[0]) for t in trades]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    if den <= 0:
        return 0.0
    return num / den