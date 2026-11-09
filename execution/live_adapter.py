"""Live/paper execution adapter (zero-dep, urllib REST)."""
import json, os, time, urllib.request, urllib.error

class LiveAdapter:
    def __init__(self, broker="binance", sandbox=True, api_key=None, api_secret=None):
        self.broker = broker
        self.sandbox = sandbox
        self.api_key = api_key or os.environ.get("API_KEY", "")
        self.api_secret = api_secret or os.environ.get("API_SECRET", "")
        self.base = "https://testnet.binance.vision" if sandbox else "https://api.binance.com"

    def _get(self, path):
        url = self.base + path
        req = urllib.request.Request(url, headers={"X-MBX-APIKEY": self.api_key} if self.api_key else {})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read())
        except Exception as e:
            return {"error": str(e)}

    def price(self, symbol="BTCUSDT"):
        d = self._get(f"/api/v3/ticker/price?symbol={symbol}")
        return float(d.get("price", 0)) if isinstance(d, dict) else 0.0

    def balance(self, asset="USDT"):
        # requires signed request; return mock in paper mode
        if self.sandbox:
            return 10000.0
        return 0.0

    def place_order(self, symbol, side, quantity, price=None):
        # paper mode: simulate; live mode: would sign & POST (requires HMAC)
        if self.sandbox or not self.api_key:
            return {"status": "FILLED (paper)", "symbol": symbol, "side": side,
                    "quantity": quantity, "price": price or self.price(symbol)}
        return {"status": "NOT_IMPLEMENTED", "note": "live signing requires HMAC-SHA256; implement per broker docs"}

    def mode(self):
        return "paper" if self.sandbox else "live"