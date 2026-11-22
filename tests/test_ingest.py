"""Risk / monitoring / bars / metrics tests."""
import unittest
import math

from risk.tail import var_historical, cvar, var_backtest
from risk.drawdown import max_drawdown, ulcer_index, max_drawdown_duration
from risk.factor import factor_exposure, multi_factor_exposure
from risk.stress import historical_replay, monte_carlo_stress
from risk.adaptive import vol_targeting, exposure_cap, kill_switch
from data.bars import volume_bars, dollar_bars, tick_bars, sessionize
from monitoring.drift import psi, ks_statistic
from monitoring.circuit_breakers import BreakerStack
from utils.metrics import deflated_sharpe, sharpe_ci
from utils.costs import cost_stack


class TestRisk(unittest.TestCase):
    def test_var_historical(self):
        rs = [0.01, -0.02, 0.005, -0.03, 0.001, -0.01, 0.02, -0.005]
        v = var_historical(rs, 0.25)
        self.assertGreaterEqual(v, 0.0)

    def test_cvar(self):
        rs = [0.01, -0.02, 0.005, -0.03, 0.001]
        self.assertGreaterEqual(cvar(rs, 0.4), 0.0)

    def test_var_backtest(self):
        lr, pval = var_backtest(5, 100, 0.05)
        self.assertGreaterEqual(pval, 0.0)
        self.assertLessEqual(pval, 1.0)

    def test_max_drawdown(self):
        eq = [100, 110, 105, 90, 95, 100]
        mdd = max_drawdown(eq)
        self.assertAlmostEqual(mdd, 0.1818, places=3)

    def test_ulcer_index(self):
        eq = [100, 110, 105, 90, 95, 100]
        self.assertGreaterEqual(ulcer_index(eq), 0.0)

    def test_max_drawdown_duration(self):
        eq = [100, 110, 105, 90, 95, 100, 112]
        self.assertGreaterEqual(max_drawdown_duration(eq), 0)

    def test_factor_exposure(self):
        r = [0.01, 0.02, -0.01, 0.015, 0.005]
        f = [0.008, 0.015, -0.008, 0.012, 0.004]
        beta = factor_exposure(r, f)
        self.assertIsInstance(beta, float)

    def test_multi_factor(self):
        r = [0.01, 0.02, -0.01, 0.015]
        factors = {"mkt": [0.008, 0.015, -0.008, 0.012], "size": [0.001, 0.002, -0.001, 0.0015]}
        out = multi_factor_exposure(r, factors)
        self.assertIn("mkt", out)
        self.assertIn("size", out)

    def test_stress(self):
        rs = [0.01, -0.005, 0.008]
        out = historical_replay(rs, [-0.05, -0.02, 0.01])
        self.assertEqual(len(out), 3)
        mc = monte_carlo_stress(rs, n_paths=5, shock=-0.1, seed=1)
        self.assertEqual(len(mc), 5)

    def test_vol_targeting(self):
        pos = vol_targeting([1.0, 2.0], 0.1, 0.2)
        self.assertAlmostEqual(pos[0], 2.0)

    def test_exposure_cap(self):
        pos = exposure_cap([3.0, 4.0], 5.0)
        self.assertAlmostEqual(sum(abs(p) for p in pos), 5.0, places=6)

    def test_kill_switch(self):
        trig, reason = kill_switch({"max_dd": 0.2, "sharpe": 1.0, "trades": 10},
                                   {"max_drawdown": 0.15, "min_sharpe": 0.5, "min_trades": 5})
        self.assertTrue(trig)
        self.assertEqual(reason, "max-drawdown-breached")


class TestBars(unittest.TestCase):
    def test_volume_bars(self):
        ticks = [{"price": 100 + i, "volume": 10, "ts": 1000 + i} for i in range(25)]
        bars = volume_bars(ticks, 50)
        self.assertGreater(len(bars), 0)
        for b in bars:
            self.assertIn("o", b)

    def test_dollar_bars(self):
        ticks = [{"price": 100.0, "volume": 10, "ts": 1000 + i} for i in range(25)]
        bars = dollar_bars(ticks, 5000)
        self.assertGreater(len(bars), 0)

    def test_tick_bars(self):
        ticks = [{"price": 100.0, "volume": 1, "ts": 1000 + i} for i in range(10)]
        bars = tick_bars(ticks, 3)
        self.assertEqual(len(bars), 4)  # 3+3+3+1

    def test_sessionize(self):
        c = [{"c": 1, "ts": 86400 + i * 60} for i in range(5)]
        out = sessionize(c, 1440)
        self.assertTrue(all("session" in r for r in out))


class TestMonitoring(unittest.TestCase):
    def test_psi_zero_same(self):
        a = [1.0, 2.0, 3.0, 4.0, 5.0] * 20
        self.assertAlmostEqual(psi(a, a), 0.0, places=6)

    def test_psi_positive_shift(self):
        a = [1.0, 2.0, 3.0, 4.0, 5.0] * 20
        b = [10.0, 11.0, 12.0, 13.0, 14.0] * 20
        self.assertGreater(psi(a, b), 0.0)

    def test_ks(self):
        self.assertGreaterEqual(ks_statistic([1, 2, 3], [4, 5, 6]), 0.0)

    def test_circuit_breaker(self):
        stack = BreakerStack()
        stack.add("trade", 2, cooldown=2)
        stack.record_failure("trade")
        stack.record_failure("trade")
        self.assertTrue(stack.any_open())
        self.assertFalse(stack.all_allow())
        stack.tick(); stack.tick()
        self.assertTrue(stack.breakers["trade"].allow())


class TestMetrics(unittest.TestCase):
    def test_deflated_sharpe(self):
        dsr = deflated_sharpe(1.5, 10, n_obs=252)
        self.assertGreaterEqual(dsr, 0.0)
        self.assertLessEqual(dsr, 1.0)

    def test_sharpe_ci(self):
        lo, hi = sharpe_ci(1.0, 252)
        self.assertLess(lo, 1.0)
        self.assertGreater(hi, 1.0)

    def test_cost_stack(self):
        self.assertEqual(cost_stack(1, 2, 3, 4), 10.0)


if __name__ == "__main__":
    unittest.main()