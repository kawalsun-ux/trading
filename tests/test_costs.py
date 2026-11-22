"""Transaction cost helpers tests."""
import unittest
from utils.costs import (spread_corwin_schultz, spread_roll, kyle_lambda,
                          impact_sqrt, cost_stack, gross_vs_net, cost_cliff_table)


class TestCosts(unittest.TestCase):
    def test_corwin_schultz_positive(self):
        highs = [10.5, 10.8, 11.0, 10.9, 11.2]
        lows = [9.8, 10.0, 10.2, 10.1, 10.4]
        s = spread_corwin_schultz(highs, lows)
        self.assertGreaterEqual(s, 0.0)

    def test_spread_roll_nonnegative(self):
        rets = [0.01, -0.005, 0.008, -0.002, 0.003]
        s = spread_roll(rets)
        self.assertGreaterEqual(s, 0.0)

    def test_kyle_lambda_basic(self):
        trades = [(0.1, 10), (0.2, 20), (-0.05, -5), (0.15, 15)]
        lam = kyle_lambda(trades)
        self.assertIsInstance(lam, float)

    def test_impact_sqrt_monotonic(self):
        a = impact_sqrt(100, 10000, 0.02)
        b = impact_sqrt(200, 10000, 0.02)
        self.assertGreaterEqual(b, a)

    def test_cost_stack(self):
        self.assertEqual(cost_stack(1.0, 2.0, 3.0, 4.0), 10.0)

    def test_gross_vs_net(self):
        net = gross_vs_net(1.0, 1.0, trades_per_year=252)
        self.assertLess(net, 1.0)

    def test_cost_cliff_table(self):
        rows = [{"freq": "daily", "sharpe_gross": 1.0, "sharpe_net": 0.3}]
        out = cost_cliff_table(rows)
        self.assertTrue(out[0]["survives"])
        self.assertAlmostEqual(out[0]["cost_drag"], 0.7)


if __name__ == "__main__":
    unittest.main()