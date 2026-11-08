"""Paper-trading example using ccxt (sandbox/testnet)."""
import ccxt

def make_exchange(name="binance", sandbox=True):
    ex = getattr(ccxt, name)({"enableRateLimit": True})
    if sandbox and hasattr(ex, "setSandboxMode"):
        ex.setSandboxMode(True)
    return ex

if __name__ == "__main__":
    ex = make_exchange("binance", sandbox=True)
    print("Markets:", len(ex.load_markets()))
    ticker = ex.fetch_ticker("BTC/USDT")
    print("BTC/USDT last:", ticker["last"])