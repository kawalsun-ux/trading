#!/usr/bin/env python3
"""Check backtest parity against golden fixtures."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
suite = unittest.defaultTestLoader.loadTestsFromName("test_backtest_parity")
res = unittest.TextTestRunner(verbosity=1).run(suite)
sys.exit(0 if res.wasSuccessful() else 1)