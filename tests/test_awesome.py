"""Tests for awesome-quant-derived additions."""
import unittest

from engines.microstructure import vpin, trade_sign, info_driven_bar_threshold
from utils.metrics import min_track_record_length, cscv_pbo, probability_backtest_overfitting
from execution.fill_simulator import simulate_fill
from scripts.audit_backtest import audit_result


class TestVPIN(unittest.TestCase):
    def test_vpin_basic(self):
        sv = [10, -5, 8, -3, 6, -7]
        v = vpin(sv, 10)
        self.assertIsNotNone(v)
        self.assertGreaterEqual(v, 0.0)
        self.assertLessEqual(v, 1.0)

    def test_vpin_tuples(self):
        sv = [(10, 1), (5, -1), (8, 1)]
        v = vpin(sv, 10)
        self.assertIsNotNone(v)

    def test_trade_sign(self):
        self.assertEqual(trade_sign(101, 100), 1)
        self.assertEqual(trade_sign(99, 100), -1)
        self.assertEqual(trade_sign(100, 100, prev_sign=-1), -1)

    def test_threshold(self):
        t = info_driven_bar_threshold([10, 20, 30], 1.5)
        self.assertAlmostEqual(t, 30.0)


class TestPBO(unittest.TestCase):
    def test_min_track_record(self):
        t = min_track_record_length(1.0)
        self.assertGreater(t, 0)

    def test_cscv_pbo(self):
        mat = [[0.01, 0.02, -0.01, 0.015],
               [0.005, 0.01, 0.00, 0.008],
               [-0.002, 0.003, -0.004, 0.001]]
        pbo = cscv_pbo(mat)
        self.assertGreaterEqual(pbo, 0.0)
        self.assertLessEqual(pbo, 1.0)

    def test_pbo_alias(self):
        self.assertEqual(probability_backtest_overfitting(1.5), 1.0)


class TestFillSimulator(unittest.TestCase):
    def test_buy_fill(self):
        r = simulate_fill({"side": "buy", "qty": 1, "price": 100}, {"h": 101, "l": 99, "c": 100})
        self.assertTrue(r["filled"])
        self.assertEqual(r["fill_price"], 100)

    def test_buy_no_fill(self):
        r = simulate_fill({"side": "buy", "qty": 1, "price": 95}, {"h": 101, "l": 99, "c": 100})
        self.assertFalse(r["filled"])

    def test_sell_fill(self):
        r = simulate_fill({"side": "sell", "qty": 1, "price": 101}, {"h": 102, "l": 99, "c": 100})
        self.assertTrue(r["filled"])


class TestAudit(unittest.TestCase):
    def test_audit_ok(self):
        res = {"trades": [{"pnl": 1.0, "entry": 100, "qty": 1, "fees": 0.1, "hold_bars": 2}],
               "metrics": {"trades": 1, "sharpe": 1.0}, "equity": [100, 101], "engine": {"entry_delay_bars": 1}}
        issues = audit_result(res)
        self.assertEqual(issues, [])

    def test_audit_fee_exceeds(self):
        res = {"trades": [{"pnl": 1.0, "entry": 100, "qty": 1, "fees": 200, "hold_bars": 2}],
               "metrics": {"trades": 1}, "equity": [100, 101]}
        issues = audit_result(res)
        self.assertTrue(any("fee-exceeds" in i for i in issues))


if __name__ == "__main__":
    unittest.main()