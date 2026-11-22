"""Transaction cost helpers (zero-dep, stdlib)."""

import math


def spread_corwin_schultz(highs, lows):
    """Corwin-Schultz (2012) spread estimator from high/low prices.

    Returns spread in basis points (approx). Empty/short input -> 0.0.
    """
    hs = [float(x) for x in (highs or [])]
    ls = [float(x) for x in (lows or [])]
    n = min(len(hs), len(ls))
    if n < 2:
        return 0.0
    # beta = sum over consecutive days of (ln(H/L))^2
    beta = 0.0
    for i in range(1, n):
        h = max(hs[i], hs[i - 1])
        l = min(ls[i], ls[i - 1])
        if h > 0 and l > 0:
            beta += (math.log(h / l)) ** 2
    # gamma = (ln(H2/L2))^2 for the two-day bar
    h2 = max(hs[-1], hs[-2]) if n >= 2 else hs[-1]
    l2 = min(ls[-1], ls[-2]) if n >= 2 else ls[-1]
    gamma = (math.log(h2 / l2)) ** 2 if (h2 > 0 and l2 > 0) else 0.0
    # alpha
    denom = 3.0 - 2.0 * math.sqrt(2.0)
    if denom <= 0:
        return 0.0
    alpha = (math.sqrt(2.0 * beta / (n - 1)) - math.sqrt(gamma)) / denom
    # clamp
    if alpha < 0:
        alpha = 0.0
    spread = 2.0 * (math.exp(alpha) - 1.0) / (1.0 + math.exp(alpha))
    return spread * 10000.0


def spread_roll(returns):
    """Roll (1984) spread estimator from returns. Returns spread in bps."""
    rs = [float(x) for x in (returns or [])]
    if len(rs) < 2:
        return 0.0
    # covariance of consecutive returns
    cov = 0.0
    n = 0
    for i in range(1, len(rs)):
        cov += rs[i] * rs[i - 1]
        n += 1
    if n == 0:
        return 0.0
    cov /= n
    if cov >= 0:
        return 0.0
    spread = 2.0 * math.sqrt(-cov)
    return spread * 10000.0


def kyle_lambda(trades):
    """Kyle's lambda: price change per unit signed volume (impact coeff).

    trades: list of (price_change, signed_volume). Returns lambda or 0.0.
    """
    if not trades or len(trades) < 2:
        return 0.0
    # OLS slope of price_change ~ signed_volume
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


def impact_sqrt(qty, adv, sigma):
    """Square-root market impact model: sigma * sqrt(qty/adv)."""
    try:
        q = float(qty); a = float(adv); s = float(sigma)
    except (TypeError, ValueError):
        return 0.0
    if a <= 0 or s < 0 or q < 0:
        return 0.0
    return s * math.sqrt(q / a) * 10000.0  # bps


def cost_stack(spread_bps=0.0, impact_bps=0.0, fee_bps=0.0, slippage_bps=0.0):
    """Total cost in bps."""
    return float(spread_bps) + float(impact_bps) + float(fee_bps) + float(slippage_bps)


def gross_vs_net(gross_sharpe, cost_drag_bps, trades_per_year=252):
    """Approximate net Sharpe from gross Sharpe and per-trade cost drag."""
    # cost drag in return units per year
    drag = (cost_drag_bps / 10000.0) * trades_per_year
    return gross_sharpe - drag


def cost_cliff_table(results_by_freq):
    """Format a list of {freq, sharpe_gross, sharpe_net} into a readable table.

    Returns list of dicts with added 'cost_drag' and 'survives' (net>0).
    """
    out = []
    for r in results_by_freq or []:
        g = float(r.get("sharpe_gross", 0.0))
        n = float(r.get("sharpe_net", 0.0))
        out.append({
            "freq": r.get("freq"),
            "sharpe_gross": g,
            "sharpe_net": n,
            "cost_drag": g - n,
            "survives": n > 0,
        })
    return out