"""Result object: a dict with attribute access (ingested from api-anything)."""

class Result(dict):
    """A call's answer as a dict with attribute access. Missing keys read as None."""

    @property
    def ok(self):
        return self.get("ok") is True

    @property
    def klass(self):
        return self.get("class")

    @property
    def reason(self):
        return self.get("reason")

    @property
    def data(self):
        return self.get("data")

    @property
    def pending(self):
        return self.get("class") == "pending"

    @property
    def job(self):
        return self.get("job")

    def raise_for_status(self):
        if self.ok:
            return self
        raise ValueError(f"{self.klass}: {self.reason}")


def deviation_bps(price, reference):
    """Signed distance of `price` from `reference` in basis points.

    Positive when price is above reference. Returns 0.0 when reference
    is non-positive so callers never divide by zero.
    """
    try:
        ref = float(reference)
        px = float(price)
    except (TypeError, ValueError):
        return 0.0
    if ref <= 0:
        return 0.0
    return (px - ref) / ref * 10000.0


def vwap_slippage_bps(achieved_price, vwap):
    """Slippage of an achieved average price versus a VWAP benchmark, bps.

    Positive means the execution was worse than the benchmark (paid more
    on a buy, received less on a sell in absolute terms). Magnitude only;
    sign of the trade is the caller's concern.
    """
    return abs(deviation_bps(achieved_price, vwap))


def time_of_day_minutes(ts, session_min=1440):
    """Minutes elapsed since the session open for a unix timestamp.

    Returns None when the timestamp is unusable, so callers can skip the
    filter rather than guess.
    """
    try:
        t = float(ts)
    except (TypeError, ValueError):
        return None
    if t <= 0:
        return None
    width = max(1, int(session_min or 1440)) * 60
    return (t % width) / 60.0


def in_session_window(ts, session_min=1440, skip_min=30):
    """True when `ts` is at least `skip_min` minutes inside the session.

    Used to avoid trading the open/close noise. Returns True when the
    timestamp is unusable so the filter degrades to 'no filter' rather
    than silently blocking everything.
    """
    m = time_of_day_minutes(ts, session_min)
    if m is None:
        return True
    if skip_min and skip_min > 0:
        if m < skip_min or m > session_min - skip_min:
            return False
    return True
