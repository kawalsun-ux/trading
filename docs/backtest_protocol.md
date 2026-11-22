# Backtest Protocol (Apex Quant)

This document fixes the invariants that make backtest results comparable and
reproducible. Any change to these conventions is a *mechanics change*, not a
parameter change, and must be recorded in the run log.

## Signal timing
- Deciding bar `i` produces a signal evaluated on `candles[lo:i+1]` with
  `lo = max(0, i - lookback + 1)`, `lookback` default 250.
- Fill occurs on bar `i + entry_delay` (default 1) at that bar's close,
  adjusted by slippage. `entry_delay=0` is same-bar fill (not default).

## Execution
- Entry price: `close * (1 + direction * slip)`, `slip = slippage_bps/10000`.
- Exit price: `close * (1 - direction * slip)`.
- Fees: `abs(notional) * fee_bps / 10000` per side.
- Quantity fixed by strategy `qty` param (default 1.0).

## Costs
- Default `cost_model="flat"`: constant `slippage_bps` + `fee_bps`.
- `cost_model="spread"`: per-bar spread via Corwin-Schultz (fallback flat).
- `cost_model="impact"`: slippage scaled by sqrt(qty/ADV).
- `dynamic_slippage`: escalate when bar volume < 20-day average pace.

## Sizing
- Fixed quantity from strategy params; position sizing helpers in `risk/position_sizing.py`.

## Data
- Candles: dicts with o/h/l/c/v/ts (or long keys). No lookahead: only bars up to `i`.
- Sessions: VWAP resets per session boundary (session_min, default 1440 min).

## Evaluation
- Metrics: trades, wins, win_rate, pf, maxDD, sharpe, cagr, avg_hold.
- Credibility: Deflated Sharpe + trial count reported (Phase 5).
- Gross-vs-net: report both when costs applied.

## Reproducibility
- Seed via `utils/reproducibility.seed_all` (Phase 7).
- Log every run via `utils.runlog.log_run`.