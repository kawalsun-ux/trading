"""Tests for Phase 3/6/8 additions."""
import unittest

from utils.features import (zscore, momentum, reversal, rolling_vol, liquidity_proxy,
                            point_in_time_align, calendar_encoding, feature_spec)
from execution.state_machine import Order, reconcile
from execution.parity import verify_parity
from execution.safety import preflight_checks, shadow_mode
from backtests.baseline import baseline_checkpoint


class TestFeatures(unittest.TestCase):
    def test_zscore(self):
        s = zscore([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], lookback=5)
        self.assertEqual(len(s), 10)
        self.assertAlmostEqual(s[0], 0.0)

    def test_momentum(self):
        m = momentum([1, 2, 3, 4, 5], lookback=2)
        self.assertEqual(m[0], 0.0)
        self.assertAlmostEqual(m[2], 3/1 - 1, places=6)

    def test_reversal(self):
        r = reversal([1, 2, 3, 4, 5], lookback=2)
        self.assertEqual(len(r), 5)

    def test_rolling_vol(self):
        v = rolling_vol([1, 2, 3, 4, 5], lookback=3)
        self.assertEqual(len(v), 5)
        self.assertGreaterEqual(v[-1], 0.0)

    def test_liquidity_proxy(self):
        lp = liquidity_proxy([2, 3, 4], [1, 2, 3], [1.5, 2.5, 3.5], [100, 100, 100])
        self.assertEqual(len(lp), 3)

    def test_point_in_time_align(self):
        out = point_in_time_align([10, 20], [2, 5])
        self.assertEqual(out[0], None)
        self.assertEqual(out[2], 10)
        self.assertEqual(out[5], 20)

    def test_calendar_encoding(self):
        s, c = calendar_encoding(86400 * 100)
        self.assertIsInstance(s, float)

    def test_feature_spec(self):
        spec = feature_spec("mom", horizon=5, driver="price", role="signal")
        self.assertEqual(spec["name"], "mom")


class TestStateMachine(unittest.TestCase):
    def test_transition(self):
        o = Order("1", "buy", 10)
        o.transition("ACKED", {})
        o.apply_fill(10)
        self.assertEqual(o.state, "FILLED")

    def test_invalid_transition(self):
        o = Order("2", "buy", 10)
        with self.assertRaises(ValueError):
            o.transition("FILLED", {})

    def test_cancel(self):
        o = Order("3", "buy", 10)
        o.cancel()
        self.assertEqual(o.state, "CANCELED")

    def test_reject(self):
        o = Order("4", "buy", 10)
        o.reject("bad")
        self.assertEqual(o.state, "REJECTED")

    def test_reconcile(self):
        local = [{"order_id": "1", "state": "FILLED"}]
        broker = [{"order_id": "1", "state": "PARTIAL"}]
        mm = reconcile(local, broker)
        self.assertEqual(len(mm), 1)
        self.assertEqual(mm[0]["issue"], "state-mismatch")

    def test_reconcile_missing(self):
        local = [{"order_id": "1", "state": "FILLED"}]
        mm = reconcile(local, [])
        self.assertEqual(mm[0]["issue"], "missing-at-broker")


class TestParity(unittest.TestCase):
    def test_verify_parity_ok(self):
        r = verify_parity([{"a": 1}], [{"a": 1}])
        self.assertTrue(r["ok"])

    def test_verify_parity_mismatch(self):
        r = verify_parity([{"a": 1}], [{"a": 2}])
        self.assertFalse(r["ok"])
        self.assertEqual(r["count"], 1)


class TestSafety(unittest.TestCase):
    def test_preflight_ok(self):
        issues = preflight_checks({"cash": 1000}, [{"qty": 1}], 100)
        self.assertEqual(issues, [])

    def test_preflight_exposure(self):
        issues = preflight_checks({"cash": 1000}, [{"qty": 200}], 100)
        self.assertIn("exposure-exceeded", issues)

    def test_shadow_mode(self):
        self.assertTrue(shadow_mode(1.0, 2.0)["diverged"])
        self.assertFalse(shadow_mode(1.0, 1.0)["diverged"])


class TestBaseline(unittest.TestCase):
    def test_baseline_ok(self):
        ok, issues = baseline_checkpoint({"trades": 10, "maxDD": 0.1, "win_rate": 0.5})
        self.assertTrue(ok)
        self.assertEqual(issues, [])

    def test_baseline_fail(self):
        ok, issues = baseline_checkpoint({"trades": 2, "maxDD": 0.6, "win_rate": 0.0})
        self.assertFalse(ok)
        self.assertIn("too-few-trades", issues)


if __name__ == "__main__":
    unittest.main()