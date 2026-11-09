"""Zero-dep web UI backend for the trading kit (stdlib only)."""
import json, os, sys, time, threading, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from http.server import HTTPServer, BaseHTTPRequestHandler
from kit import safety, backtest, report, store, pool, dashboard
from kit.safety import SafetyError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
PORT = int(os.environ.get("PORT", "8765"))

# In-memory config
CONFIG = {
    "mode": "paper", "broker": "binance", "sandbox": True,
    "max_position_pct": 0.1, "max_drawdown_pct": 0.15, "stop_loss_pct": 0.02,
    "slippage_pct": 0.005, "quote_max_age": 10,
}

class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, obj, status=200):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/" or path == "/index.html":
            self._file("index.html", "text/html")
        elif path.startswith("/static/"):
            self._file(path[len("/static/"):], None)
        elif path == "/api/health":
            self._json({"ok": True, "mode": CONFIG["mode"]})
        elif path == "/api/config":
            self._json(CONFIG)
        elif path == "/api/trades":
            self._json({"trades": store.recent(50)})
        elif path == "/api/strategies":
            self._json({"strategies": [
                {"id": "ma_crossover", "name": "MA Crossover", "type": "trend"},
                {"id": "rsi_bb", "name": "RSI + Bollinger Bands", "type": "mean_reversion"},
                {"id": "momentum", "name": "Momentum", "type": "trend"},
                {"id": "mean_reversion", "name": "Mean Reversion (RSI)", "type": "mean_reversion"},
                {"id": "breakout", "name": "Breakout", "type": "breakout"},
                {"id": "pairs", "name": "Pairs Trading (Spread)", "type": "pairs"},
                {"id": "arb_spread", "name": "Arbitrage Spread", "type": "arbitrage"},
                {"id": "scalp_micro", "name": "Scalping Micro-Profit", "type": "scalping"},
            ]})
        elif path.startswith("/ws/"):
            self._websocket(path)
        elif path == "/api/pools":
            # mock multi-exchange prices
            import random
            base = 100.0
            exchanges = ["binance", "kraken", "coinbase", "okx"]
            data = {}
            for ex in exchanges:
                data[ex] = round(base * (1 + random.uniform(-0.003, 0.003)), 4)
            best_buy = min(data, key=lambda k: data[k])
            best_sell = max(data, key=lambda k: data[k])
            spread = data[best_sell] - data[best_buy]
            spread_pct = spread / data[best_buy] * 100
            self._json({"prices": data, "best_buy": best_buy, "best_sell": best_sell,
                        "spread": round(spread, 4), "spread_pct": round(spread_pct, 4),
                        "profitable": spread_pct > 0.1})
        elif path == "/api/walkforward":
            self._json({"status": "run via CLI", "file": "reports/walk_forward.csv"})
        elif path == "/api/live/price":
            from execution.live_adapter import LiveAdapter
            ad = LiveAdapter(sandbox=CONFIG.get("sandbox", True))
            sym = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("symbol", ["BTCUSDT"])[0]
            self._json({"symbol": sym, "price": ad.price(sym), "mode": ad.mode()})
        else:
            self.send_response(404); self.end_headers()

    def _file(self, name, ctype):
        fpath = os.path.join(STATIC, name) if not name.endswith(".html") else os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
        if name == "index.html":
            fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
        if not os.path.exists(fpath):
            self.send_response(404); self.end_headers(); return
        with open(fpath, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self._cors()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _websocket(self, path):
        key = self.headers.get("Sec-WebSocket-Key")
        if not key:
            self.send_response(400); self.end_headers(); return
        import base64, hashlib
        accept = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
        self.send_response(101)
        self.send_header("Upgrade", "websocket")
        self.send_header("Connection", "Upgrade")
        self.send_header("Sec-WebSocket-Accept", accept)
        self.end_headers()
        upstream = None
        if path == "/ws/binance":
            try:
                from kit.ws_client import connect, recv_frame
                upstream, _ = connect("wss://stream.binance.com:9443/ws/btcusdt@ticker", timeout=3)
            except Exception as e:
                upstream = None
        elif path == "/ws/london":
            import os
            url = os.environ.get("LONDON_WS_URL")
            if url:
                try:
                    from kit.ws_client import connect
                    upstream, _ = connect(url, timeout=3)
                except Exception:
                    upstream = None
        elif path == "/ws/orderbook":
            try:
                from kit.ws_client import connect
                upstream, _ = connect("wss://stream.binance.com:9443/ws/btcusdt@depth20@100ms", timeout=3)
            except Exception:
                upstream = None
        # relay or mock
        import json as _j, time as _t, random as _r
        try:
            if upstream is not None:
                from kit.ws_client import recv_frame
                for _ in range(60):
                    fr = recv_frame(upstream, timeout=2)
                    if fr is None:
                        break
                    op, payload, fin = fr
                    if op == 1:  # text
                        try:
                            d = json.loads(payload)
                            if "c" in d:
                                msg = _j.dumps({"type": "price", "source": "binance", "symbol": d.get("s"), "price": float(d.get("c")), "ts": _t.time()})
                            elif "bids" in d or "b" in d:
                                bids = d.get("bids") or d.get("b", [])
                                asks = d.get("asks") or d.get("a", [])
                                msg = _j.dumps({"type": "orderbook", "bids": bids[:10], "asks": asks[:10], "ts": _t.time()})
                            else:
                                msg = payload.decode("utf-8", "replace")
                            self.wfile.write(self._ws_frame(msg)); self.wfile.flush()
                        except Exception:
                            self.wfile.write(self._ws_frame(payload.decode("utf-8","replace"))); self.wfile.flush()
                    elif op == 8:
                        break
            else:
                # mock stream (london edge, orderbook, or fallback)
                for i in range(60):
                    if path == "/ws/london":
                        msg = _j.dumps({"type": "edge", "session": "london", "signal": _r.choice(["buy","sell","hold"]), "strength": round(_r.random(),3), "ts": _t.time()})
                    elif path == "/ws/orderbook":
                        mid = 100.0
                        bids = [[round(mid - i*0.05 - _r.random()*0.02, 4), round(_r.uniform(0.5, 5), 3)] for i in range(10)]
                        asks = [[round(mid + i*0.05 + _r.random()*0.02, 4), round(_r.uniform(0.5, 5), 3)] for i in range(10)]
                        msg = _j.dumps({"type": "orderbook", "bids": bids, "asks": asks, "ts": _t.time()})
                    else:
                        prices = {ex: round(100.0*(1+_r.uniform(-0.003,0.003)),4) for ex in ["binance","kraken","coinbase","okx"]}
                        msg = _j.dumps({"type": "price", "source": "mock", "prices": prices, "ts": _t.time()})
                    self.wfile.write(self._ws_frame(msg)); self.wfile.flush()
                    _t.sleep(1)
            self.wfile.write(b"\x88\x00"); self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, Exception):
            pass
        finally:
            try:
                if upstream: upstream.close()
            except Exception:
                pass
            try:
                self.wfile.close()
            except Exception:
                pass

    def _ws_frame(self, text):
        import struct
        b = text.encode()
        header = bytes([0x81])  # FIN + text
        if len(b) < 126:
            header += bytes([len(b)])
        elif len(b) < 65536:
            header += bytes([126]) + struct.pack("!H", len(b))
        else:
            header += bytes([127]) + struct.pack("!Q", len(b))
        return header + b

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        body = self._body()
        if path == "/api/safety/check":
            try:
                token = body.get("token", "TKN")
                known = set(body.get("known", [token]))
                balance = float(body.get("balance", 0))
                required = float(body.get("required", 1))
                quote_ts = float(body.get("quote_ts", time.time()))
                expected = float(body.get("expected", 100))
                actual = float(body.get("actual", 100))
                max_age = float(body.get("max_age", CONFIG["quote_max_age"]))
                max_slip = float(body.get("max_slippage", CONFIG["slippage_pct"]))
                safety.run_all(token, known, balance, required, quote_ts, expected, actual,
                               max_age_sec=max_age, max_slippage_pct=max_slip)
                self._json({"ok": True, "message": "ALL 4 CHECKS PASSED"})
            except SafetyError as e:
                self._json({"ok": False, "message": str(e)}, 400)
        elif path == "/api/backtest":
            import random
            n = int(body.get("n", 200))
            strat = body.get("strategy", "ma_crossover")
            prices = [100 + i*0.1 + (i % 7 - 3)*0.5 for i in range(n)]
            if strat == "scalp_micro":
                prices = [100 + (i % 20 - 10)*0.05 for i in range(n)]
            elif strat == "arb_spread":
                prices = [100 + (i % 5)*0.2 for i in range(n)]
            def rule(i, ps, pos):
                if i > 5 and ps[i] > ps[i-5] and not pos: return 'buy'
                if i > 5 and ps[i] < ps[i-5] and pos: return 'sell'
                return 'hold'
            res = backtest.run_backtest(prices, rule)
            s = report.summary(res)
            self._json({"strategy": strat, "metrics": s, "prices": prices,
                        "trades": res["trades"][:50]})
        elif path == "/api/trade":
            store.log_trade(body.get("action", "buy"), body.get("token", "TKN"),
                            float(body.get("price", 0)), float(body.get("units", 0)),
                            status=body.get("status", "filled"), note=body.get("note", ""))
            self._json({"ok": True})
        elif path == "/api/config":
            CONFIG.update(body)
            self._json(CONFIG)
        elif path == "/api/live/order":
            from execution.live_adapter import LiveAdapter
            ad = LiveAdapter(sandbox=CONFIG.get("sandbox", True))
            r = ad.place_order(body.get("symbol", "BTCUSDT"), body.get("side", "buy"),
                               float(body.get("quantity", 0)), body.get("price"))
            self._json(r)
        elif path == "/api/arb/execute":
            # mock arbitrage execution with safety check
            try:
                token = body.get("token", "TKN")
                known = set(body.get("known", [token]))
                balance = float(body.get("balance", 10))
                required = float(body.get("required", 1))
                quote_ts = float(body.get("quote_ts", time.time()))
                expected = float(body.get("expected", 100))
                actual = float(body.get("actual", 100))
                safety.run_all(token, known, balance, required, quote_ts, expected, actual)
                store.log_trade("arb", token, actual, float(body.get("units", 1)), status="filled", note="arb executed")
                self._json({"ok": True, "message": "Arbitrage executed (test mode)"})
            except SafetyError as e:
                store.log_trade("arb", body.get("token", "TKN"), float(body.get("actual", 0)), 0, status="rejected", note=str(e))
                self._json({"ok": False, "message": str(e)}, 400)
        else:
            self.send_response(404); self.end_headers()

    def log_message(self, *a):
        pass

if __name__ == "__main__":
    store.init()
    httpd = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Trading UI server running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()