"""Backtest parity: lock current engine outputs as golden fixtures."""
import json, math, os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.backtest import run_backtest

EXPECTED = {
    "vwap_trend": {"trades": 1, "sharpe": -92.32330340634499},
    "vwap_mean_reversion": {"trades": 1, "sharpe": 85.4379524625022},
    "absorption": {"trades": 0, "sharpe": 0.0},
    "zscore_reversion": {"trades": 0, "sharpe": 0.0},
}


def _candles():
    base_ts = 86400 + 35 * 60
    candles = []
    price = 100.0
    for i in range(300):
        price += 0.05 if i < 150 else -0.03
        vol = 1000 + 500 * math.sin(i / 10.0)
        candles.append({"o": price - 0.1, "h": price + 0.2, "l": price - 0.2,
                        "c": price, "v": vol, "ts": base_ts + i * 60})
    return candles


class BacktestParity(unittest.TestCase):
    def test_outputs_unchanged(self):
        candles = _candles()
        for kind, exp in EXPECTED.items():
            res = run_backtest(candles, kind, {"qty": 1.0, "max_spread_bps": 1000},
                               fee_bps=1, slippage_bps=1)
            self.assertEqual(len(res["trades"]), exp["trades"],
                             msg=f"{kind} trade count changed")
            self.assertAlmostEqual(res["metrics"].get("sharpe", 0.0), exp["sharpe"],
                                   places=6, msg=f"{kind} sharpe changed")


if __name__ == "__main__":
    unittest.main()