"""Additional market data sources (zero-dep, stdlib)."""
import os, json, urllib.request, urllib.parse

def equities_yahoo(symbol, start="2018-01-01"):
    # minimal: return synthetic if network unavailable
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5y&interval=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            closes = d["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            return [c for c in closes if c is not None]
    except Exception:
        return []

def crypto_price(symbol="BTCUSDT"):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        with urllib.request.urlopen(url, timeout=10) as r:
            return float(json.loads(r.read())["price"])
    except Exception:
        return None

def from_csv(path, date_col="Date"):
    import csv
    rows = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows