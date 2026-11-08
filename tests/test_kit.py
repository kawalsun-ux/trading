import sys, os, unittest, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import safety, backtest, report, store

class TestSafety(unittest.TestCase):
    def test_all_pass(self):
        safety.run_all("MINT1", {"MINT1"}, 10.0, 1.0, time.time(), 100.0, 100.5, max_slippage_pct=0.01)
    def test_wrong_token(self):
        with self.assertRaises(safety.SafetyError):
            safety.run_all("X", {"MINT1"}, 10.0, 1.0, time.time(), 100.0, 100.0)
    def test_low_balance(self):
        with self.assertRaises(safety.SafetyError):
            safety.run_all("MINT1", {"MINT1"}, 0.5, 1.0, time.time(), 100.0, 100.0)
    def test_stale_quote(self):
        with self.assertRaises(safety.SafetyError):
            safety.run_all("MINT1", {"MINT1"}, 10.0, 1.0, time.time()-100, 100.0, 100.0, max_age_sec=10)
    def test_slippage(self):
        with self.assertRaises(safety.SafetyError):
            safety.run_all("MINT1", {"MINT1"}, 10.0, 1.0, time.time(), 100.0, 110.0, max_slippage_pct=0.01)

class TestBacktest(unittest.TestCase):
    def test_runs(self):
        prices = [100 + i*0.5 for i in range(50)]
        def rule(i, ps, pos):
            if i > 2 and ps[i] > ps[i-1] and not pos: return 'buy'
            if i > 2 and ps[i] < ps[i-1] and pos: return 'sell'
            return 'hold'
        res = backtest.run_backtest(prices, rule)
        self.assertIn("final", res)
        s = report.summary(res)
        self.assertIn("sharpe", s)

class TestStore(unittest.TestCase):
    def test_log_and_read(self):
        store.log_trade("buy", "SOL", 100.0, 1.0, note="test")
        rows = store.recent(5)
        self.assertTrue(len(rows) >= 1)

if __name__ == "__main__":
    unittest.main()