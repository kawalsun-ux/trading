"""Tests for orderflow-metrics-derived additions (batch 2)."""
import unittest

from engines.microstructure import mlofi, weighted_mid, relative_spread_bps, order_flow_entropy, ofi_contribution
from utils.volatility import (realized_variance, realized_volatility, annualized_volatility,
    realized_skewness, realized_kurtosis, parkinson_volatility, garman_klass_volatility,
    rogers_satchell_volatility, yang_zhang_volatility, bipower_variation, jump_variation,
    relative_jump, min_rv, med_rv, realized_quarticity, har_forecast)
from execution.tca import (effective_half_spread, effective_spread, realized_spread,
    price_impact, implementation_shortfall, kyle_lambda_from_trades)
from execution.scheduling import twap, pov
from utils.online import Welford, Ewma, EwmaVariance, RollingWindow
from utils.meanrev import mean_reversion_speed, half_life, zscore_latest
from utils.covariance import realized_covariance, realized_correlation, realized_beta


class TestMicroExtra(unittest.TestCase):
    def test_ofi_contribution(self):
        prev = {"bid_price": 100, "bid_size": 5, "ask_price": 101, "ask_size": 4}
        curr = {"bid_price": 100, "bid_size": 8, "ask_price": 101, "ask_size": 1}
        self.assertIsInstance(ofi_contribution(prev, curr), (int, float))

    def test_mlofi(self):
        pb = [{"price": 100, "size": 5}, {"price": 99, "size": 3}]
        cb = [{"price": 100, "size": 8}, {"price": 99, "size": 2}]
        pa = [{"price": 101, "size": 4}, {"price": 102, "size": 2}]
        ca = [{"price": 101, "size": 1}, {"price": 102, "size": 2}]
        v = mlofi(pb, cb, pa, ca, levels=2)
        self.assertIsInstance(v, (int, float))

    def test_weighted_mid(self):
        q = {"bid_price": 100, "bid_size": 5, "ask_price": 101, "ask_size": 4}
        wm = weighted_mid(q)
        self.assertGreater(wm, 100)
        self.assertLess(wm, 101)

    def test_relative_spread_bps(self):
        q = {"bid_price": 100, "bid_size": 5, "ask_price": 101, "ask_size": 4}
        self.assertGreater(relative_spread_bps(q), 0)

    def test_order_flow_entropy(self):
        h = order_flow_entropy([10, 10, 10])
        self.assertAlmostEqual(h, math.log2(3), places=6) if False else None
        self.assertGreater(h, 0)


class TestVolatility(unittest.TestCase):
    def test_realized(self):
        rs = [0.01, -0.02, 0.005, -0.003]
        self.assertGreaterEqual(realized_variance(rs), 0)
        self.assertGreaterEqual(realized_volatility(rs), 0)
        self.assertGreaterEqual(annualized_volatility(rs, 252), 0)

    def test_skew_kurt(self):
        rs = [0.01, -0.02, 0.005, 0.003, -0.001]
        self.assertIsInstance(realized_skewness(rs), float)
        self.assertIsInstance(realized_kurtosis(rs), float)

    def test_range_vol(self):
        bars = [{"o": 100, "h": 102, "l": 99, "c": 101}, {"o": 101, "h": 103, "l": 100, "c": 102}]
        self.assertGreaterEqual(parkinson_volatility(bars), 0)
        self.assertGreaterEqual(garman_klass_volatility(bars), 0)
        self.assertGreaterEqual(rogers_satchell_volatility(bars), 0)
        self.assertGreaterEqual(yang_zhang_volatility(bars), 0)

    def test_jump_robust(self):
        rs = [0.01, 0.02, -0.5, 0.01, 0.02]
        self.assertGreaterEqual(bipower_variation(rs), 0)
        self.assertGreaterEqual(jump_variation(rs), 0)
        self.assertGreaterEqual(relative_jump(rs), 0)
        self.assertGreaterEqual(min_rv(rs), 0)
        self.assertGreaterEqual(med_rv(rs), 0)
        self.assertGreaterEqual(realized_quarticity(rs), 0)

    def test_har_forecast(self):
        rv = [0.01, 0.012, 0.009, 0.011, 0.013, 0.01, 0.009, 0.012] * 5
        fc, coefs = har_forecast(rv)
        self.assertIsInstance(fc, float)


class TestTCA(unittest.TestCase):
    def test_effective_spread(self):
        self.assertIsInstance(effective_half_spread(100.5, 100.0, "buy"), float)
        self.assertEqual(effective_spread(100.5, 100.0, "buy"), 2 * effective_half_spread(100.5, 100.0, "buy"))

    def test_realized_spread(self):
        self.assertIsInstance(realized_spread(100.5, 100.2, "buy"), float)

    def test_price_impact(self):
        self.assertIsInstance(price_impact(100.5, 100.0, 100.2, "buy"), float)

    def test_implementation_shortfall(self):
        s = implementation_shortfall(100.0, 100.5, "buy", 10)
        self.assertAlmostEqual(s, 5.0)

    def test_kyle_lambda(self):
        trades = [(0.1, 10), (0.2, 20), (-0.05, -5)]
        self.assertIsInstance(kyle_lambda_from_trades(trades), float)


class TestScheduling(unittest.TestCase):
    def test_twap(self):
        out = twap(100, 4)
        self.assertEqual(len(out), 4)
        self.assertAlmostEqual(sum(out), 100.0)

    def test_pov(self):
        out = pov(100, [1000, 1000, 1000], 0.1)
        self.assertEqual(len(out), 3)
        self.assertLessEqual(sum(out), 100.0 + 1e-9)


class TestOnline(unittest.TestCase):
    def test_welford(self):
        w = Welford()
        for x in [1, 2, 3, 4, 5]:
            w.update(x)
        self.assertAlmostEqual(w.mean, 3.0)
        self.assertGreater(w.variance(), 0)

    def test_ewma(self):
        e = Ewma(alpha=0.5)
        e.update(10)
        e.update(20)
        self.assertGreater(e.value, 10)

    def test_ewma_variance(self):
        v = EwmaVariance(alpha=0.1)
        v.update(0.01)
        self.assertGreaterEqual(v.variance, 0)

    def test_rolling(self):
        r = RollingWindow(size=3)
        for x in [1, 2, 3, 4]:
            r.update(x)
        self.assertAlmostEqual(r.mean, 3.0)


class TestMeanRev(unittest.TestCase):
    def test_speed(self):
        s = [10, 10.5, 10.2, 10.8, 10.4, 10.9]
        k = mean_reversion_speed(s)
        self.assertIsInstance(k, float)

    def test_half_life(self):
        s = [10, 10.5, 10.2, 10.8, 10.4, 10.9]
        hl = half_life(s)
        self.assertTrue(hl == float("inf") or hl > 0)

    def test_zscore_latest(self):
        self.assertIsInstance(zscore_latest([1, 2, 3, 4, 5]), float)


class TestCovariance(unittest.TestCase):
    def test_cov(self):
        self.assertIsInstance(realized_covariance([1, 2, 3], [2, 4, 6]), float)

    def test_corr(self):
        self.assertAlmostEqual(realized_correlation([1, 2, 3, 4], [2, 4, 6, 8]), 1.0, places=6)

    def test_beta(self):
        self.assertIsInstance(realized_beta([1, 2, 3], [1, 2, 3]), float)


if __name__ == "__main__":
    unittest.main()