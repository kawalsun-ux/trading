"""Options/volatility helpers (zero-dep, stdlib + math)."""

import math
import random


def straddle_price(vol=0.2, time=1.0, forward=1.0):
    """Closed-form ATMF straddle approximation.

    STRADDLE_ATMF ~ (2 / sqrt(2*pi)) * F * sigma * sqrt(T)
    """
    if vol is None or time is None or vol < 0 or time < 0:
        return 0.0
    return (2.0 / math.sqrt(2.0 * math.pi)) * float(forward) * float(vol) * math.sqrt(float(time))


def straddle_mc(vol=0.2, time=1.0, mc_paths=1000, seed=None):
    """Monte-Carlo ATMF straddle price (geometric Brownian, terminal abs deviation)."""
    if vol is None or time is None or vol < 0 or time < 0 or mc_paths <= 0:
        return 0.0
    if seed is not None:
        random.seed(seed)
    daily_vol = float(vol) / math.sqrt(252.0)
    n_days = int(round(float(time) * 252.0))
    if n_days <= 0:
        return 0.0
    total = 0.0
    for _ in range(int(mc_paths)):
        prod = 1.0
        for _ in range(n_days):
            prod *= (1.0 + random.gauss(0.0, daily_vol))
        total += abs(prod - 1.0)
    return total / float(mc_paths)


def straddle_mc_fast(vol=0.2, time=1.0, mc_paths=10000, seed=None):
    """Vectorised-ish MC using a flat list (still stdlib, no numpy)."""
    if vol is None or time is None or vol < 0 or time < 0 or mc_paths <= 0:
        return 0.0
    if seed is not None:
        random.seed(seed)
    daily_vol = float(vol) / math.sqrt(252.0)
    n_days = int(round(float(time) * 252.0))
    if n_days <= 0:
        return 0.0
    total = 0.0
    for _ in range(int(mc_paths)):
        prod = 1.0
        for _ in range(n_days):
            prod *= (1.0 + random.gauss(0.0, daily_vol))
        total += abs(prod - 1.0)
    return total / float(mc_paths)


def implied_vol_from_straddle(price, time=1.0, forward=1.0):
    """Invert the closed-form straddle price to an implied vol (approx)."""
    if price is None or time is None or time <= 0 or forward is None or forward <= 0:
        return None
    denom = (2.0 / math.sqrt(2.0 * math.pi)) * float(forward) * math.sqrt(float(time))
    if denom <= 0:
        return None
    return float(price) / denom