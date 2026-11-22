"""Credit-risk helpers (zero-dep, stdlib). Altman Z'' score from fundamentals."""

import os
import json
import time
import urllib.request
import urllib.parse


ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"


def _av_get(function, ticker, api_key, sleep=0.6):
    time.sleep(sleep)
    params = {"function": function, "symbol": ticker, "apikey": api_key}
    url = ALPHA_VANTAGE_BASE_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def altman_z_double_prime(ticker, api_key=None):
    """Altman Z'' (Double Prime) score from Alpha Vantage fundamentals.

    Returns a float, or None if data is unavailable. Uses the public
    "demo" key by default (only real data for "IBM").
    """
    key = api_key or os.environ.get("ALPHA_VANTAGE_API_KEY", "demo")
    try:
        income = _av_get("INCOME_STATEMENT", ticker, key)["annualReports"][0]
        balance = _av_get("BALANCE_SHEET", ticker, key)["annualReports"][0]
        overview = _av_get("OVERVIEW", ticker, key)
    except Exception:
        return None
    try:
        total_assets = float(balance["totalAssets"])
        if total_assets <= 0:
            return None
        x1 = (float(balance["totalCurrentAssets"])
              - float(balance["totalCurrentLiabilities"])) / total_assets
        x2 = float(balance["retainedEarnings"]) / total_assets
        x3 = float(income["ebit"]) / total_assets
        total_liab = float(balance["totalLiabilities"])
        if total_liab <= 0:
            return None
        x4 = float(overview["MarketCapitalization"]) / total_liab
    except (KeyError, TypeError, ValueError):
        return None
    return 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4


# Adjusted-Z threshold table (Altman) -> implied rating.
_Z_MAP = [8.15, 7.6, 7.3, 7.0, 6.85, 6.65, 6.4, 6.25, 5.85, 5.65, 5.25,
          4.95, 4.75, 4.5, 4.15, 3.75, 3.2, 2.5, 1.75]
_RATINGS = ["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-",
            "BB+", "BB", "BB-", "B+", "B", "B-", "CCC+", "CCC", "CCC-", "D"]


def implied_rating(z):
    """Map an Altman Z'' score to an implied credit rating string."""
    if z is None:
        return None
    adj = 3.25 + float(z)
    eligible = [v for v in _Z_MAP if v < adj]
    if not eligible:
        return _RATINGS[-1]
    threshold = max(eligible)
    idx = _Z_MAP.index(threshold)
    return _RATINGS[idx]


def credit_verdict(z):
    """Coarse health verdict from an Altman Z'' score."""
    if z is None:
        return "unknown"
    if z > 2.6:
        return "healthy"
    if z >= 1.1:
        return "grey"
    return "at-risk"