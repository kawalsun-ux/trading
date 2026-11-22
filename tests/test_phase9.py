"""Tests for awesome-quant gap-fill additions."""
import unittest, math, tempfile, os

from risk.stops import trailing_stop, atr_stop, chandelier_stop, time_stop
from risk.correlation import pairwise_correlations, correlation_limit_check
from utils.metrics import bootstrap_ci_sharpe
from risk.stress import entropy_pooling_weights
from utils.audit_log import append, verify


class TestStops(unittest.TestCase):
    def test_trailing_stop(self):
        ts = trailing_stop([10, 12, 11, 13], 0.05)
        self.assertEqual(len(ts), 4)
        self.assertAlmostEqual(ts[0], 9.5)

    def test_atr_stop(self):
        out = atr_stop([100, 101], [2, 2], multiplier=2.0, side="long")
        self.assertAlmostEqual(out[0], 96.0)

    def test_chandelier_stop(self):
        out = chandelier_stop([10, 11, 12], [1, 1, 1], multiplier=2.0, lookback=3)
        self.assertEqual(len(out), 3)

    def test_time_stop(self):
        self.assertTrue(time_stop(0, 5, 5))
        self.assertFalse(time_stop(0, 4, 5))


class TestCorrelation(unittest.TestCase):
    def test_pairwise(self):
        m = {"a": [1, 2, 3, 4], "b": [2, 4, 6, 8]}
        out = pairwise_correlations(m)
        self.assertAlmostEqual(out[("a", "b")], 1.0, places=6)

    def test_limit_check(self):
        m = {"a": [1, 2, 3, 4], "b": [2, 4, 6, 8]}
        issues = correlation_limit_check(m, threshold=0.9)
        self.assertEqual(len(issues), 1)


class TestBootstrap(unittest.TestCase):
    def test_bootstrap_ci(self):
        rs = [0.01, -0.005, 0.008, 0.003, -0.002, 0.006] * 10
        lo, hi = bootstrap_ci_sharpe(rs, n_bootstrap=50, seed=1)
        self.assertLessEqual(lo, hi)


class TestEntropyPooling(unittest.TestCase):
    def test_weights_sum(self):
        rs = [0.01, -0.005, 0.008, 0.003]
        w = entropy_pooling_weights(rs, 0.004)
        self.assertAlmostEqual(sum(w), 1.0, places=6)
        self.assertEqual(len(w), len(rs))


class TestAuditLog(unittest.TestCase):
    def test_verify(self):
        fd, path = tempfile.mkstemp()
        os.close(fd)
        os.remove(path)
        append(path, {"a": 1})
        append(path, {"b": 2})
        ok, issues = verify(path)
        self.assertTrue(ok)
        self.assertEqual(issues, [])
        # tamper
        with open(path) as f:
            lines = f.readlines()
        lines[0] = lines[0].replace('"a": 1', '"a": 9')
        with open(path, "w") as f:
            f.writelines(lines)
        ok2, issues2 = verify(path)
        self.assertFalse(ok2)
        os.remove(path)


if __name__ == "__main__":
    unittest.main()