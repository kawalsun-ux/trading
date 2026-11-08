"""Pool price reader (mock + simple HTTP)."""
import json, urllib.request, time, random

def mock_pool_price(base=100.0, jitter=0.01):
    return base * (1 + random.uniform(-jitter, jitter))

def fetch_price_coingecko(coin_id="solana", vs="usd"):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            d = json.loads(r.read())
            return float(d[coin_id][vs])
    except Exception:
        return None