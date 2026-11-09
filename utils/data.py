"""Market data helpers (zero-dep, stdlib + ingested data/feeds)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.feeds import synthetic_tick, live_venue_books, fetch_venue_book

def load_ohlcv_synthetic(symbol="SPY", n=200, start_price=100.0):
    """Generate synthetic OHLCV (zero-dep, no network)."""
    prices = []
    p = start_price
    for i in range(n):
        p = p * (1 + ( (i*7+3) % 11 - 5) * 0.002)
        prices.append(round(p, 4))
    return prices

def live_prices(symbols):
    try:
        return live_venue_books(symbols)
    except Exception:
        return {}