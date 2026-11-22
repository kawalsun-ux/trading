# Trading Setup (template)

Versioned decision-time specification. All fields required for a comparable run.

- **Tradable universe**: symbols, venues, asset classes
- **Decision schedule**: bar frequency, session, time-of-day filter
- **Information set**: admissible data as of decision time (point-in-time)
- **Score-to-trade mapping**: threshold, sizing rule
- **Constraints**: position limits, exposure caps, leverage
- **Costs**: fee_bps, slippage_bps, cost_model, spread assumption
- **Evaluation metrics**: Sharpe, maxDD, win_rate, turnover, DSR
- **Baseline checkpoint**: timing, coverage, trading-intensity sanity checks