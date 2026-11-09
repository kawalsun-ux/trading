# Trading R&D Environment

Multi-language (Python-first) research & development workspace for trading
strategies and market execution.

## Layout
- `data/raw`      - raw downloaded market data
- `data/processed`- cleaned/feature data
- `data/cache`    - cached API responses
- `strategies`    - strategy definitions
- `backtests`     - backtest scripts & results
- `notebooks`     - Jupyter research notebooks
- `execution`     - live/paper order routing
- `risk`          - position sizing, VaR, limits
- `utils`         - data loaders, indicators, helpers
- `configs`       - broker/API/strategy configs
- `logs`          - run logs
- `reports`       - performance reports

## Quick start
```bash
cd ~/trading
python web/run.sh              # web UI at http://localhost:8765
jupyter lab notebooks/        # research
python backtests/run_backtest.py   # example backtest
python run_all.py              # full pipeline
```

## Installed stack
Python: pandas, numpy, scipy, scikit-learn, matplotlib, plotly, yfinance,
ccxt, backtrader, pandas-ta, ta, quantstats, seaborn
Plus: Node.js, Go, Rust, Java, C/C++, Ruby, PHP, Lua, Zig, Perl, Make, CMake.
"""