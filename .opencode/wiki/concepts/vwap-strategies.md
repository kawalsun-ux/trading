---
title: VWAP Strategies Research for Apex Quant
tags: [trading, vwap, strategy, research, apex-quant]
sourceRefs:
  - https://ninjatrader.com/futures/blogs/vwap-strategies-futures/
  - https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4631351
  - https://www.quantifiedstrategies.com/volume-weighted-average-price
  - https://www.quantifiedstrategies.com/vwap-trading-strategy/
  - https://www.sciencedirect.com/science/article/pii/S0378426607003226
  - https://arxiv.org/html/2502.13722v2
  - https://arxiv.org/html/2502.18177
  - https://arxiv.org/html/2503.02680v1
  - https://pyquantlab.medium.com/vwap-anchored-breakout-session-vs-anchored-vwap-on-aapl-intraday-53fefc20bdd9
  - https://pages.stern.nyu.edu/~jhasbrou/Teaching/POST%202020%20Fall/powerpoints/VWAP%20Strategies.pdf
lastReviewed: 2026-11-22
---

# VWAP Strategies Research for Apex Quant

Research-only (no code yet). Purpose: identify improvements to Apex Quant (`/mnt/c/Users/user/Documents/projects/trading`) using Volume-Weighted Average Price (VWAP) strategies.

## 1. What VWAP Is
VWAP = cumulative (typical price × volume) / cumulative volume, reset each session. Intraday fair-value benchmark; institutional algos defend it, creating self-reinforcing support/resistance. Not a forecast.

## 2. Strategy Families (with evidence)

| Family | Logic | Evidence |
|---|---|---|
| Trend filter | Long above VWAP, short below; pullbacks to VWAP = entries | NinjaTrader; SSRN Zarattini & Aziz QQQ: $25k→$192.6k (671%), Sharpe 2.1, max DD 9.4% vs buy-and-hold 126%/37% DD |
| Mean reversion | Fade moves stretched >1.5σ from VWAP back to line; stop beyond extreme | QuantEngines ES futures 2018–2025; Schwab intraday |
| SD bands | 1σ/2σ/3σ envelopes; entries at band tags, exits at VWAP | NinjaTrader; ~68%/95% volume containment |
| Break & retest | Breakout above VWAP → pullback to VWAP → long on support hold | Britannica |
| Anchored VWAP (AVWAP) | Reset VWAP at key event (earnings low, capitulation) | Britannica; PyQuantLab AAPL: session VWAP won (CAGR 29.8%, Sharpe 1.88) vs weekly-anchored (CAGR −34.8%) |
| Execution slicing | Match trade rate to historical intraday volume profile; adaptive | Hasbrouck NYU; ScienceDirect "Improving VWAP strategies" |
| Dynamic/ML VWAP | RNN/Transformer volume allocation; slippage ~20–47% better | arXiv 2502.13722, 2502.18177, 2503.02680 |
| Deep RL allocation | Macro-Meta-Micro hierarchical RL for parent/child slicing | IEEE 2024; arXiv 2212.14670 |

## 3. Apex Quant Relevant Modules
- `engines/backtest.py` — bar loop with pending-order delay
- `utils/indicators` — indicator home
- `data/feeds.py` — data ingestion
- `brokers/*`, `risk/`, `strategies/` (ma_crossover, template), `execution/`, `web/server.py`, `utils/result.py`

## 4. Improvement Possibilities (implemented 2026-11-22)

Implemented in `engines/signals.py` (live + backtest via `preview_signal`):
- `vwap_trend` — session-VWAP trend filter (pullback entries).
- `vwap_mean_reversion` — fade at ±entry_sigma with reversal + time filter.
- Pre-existing: `vwap_pullback`, `vwap_bands` (session VWAP, SD bands, regime + stop filters).

Supporting module: `engines/vwap.py` (session VWAP, bands, anchored VWAP, vwap_state).

### A. Indicators & data layer
- Add VWAP + SD bands (1σ/2σ/3σ) and Anchored VWAP (event-anchored) to `utils/indicators`.
- Add intraday volume profile (30-min buckets) to `data/`.
- Extend `data/feeds.py` for intraday (5-min) bars — VWAP needs intraday.

### B. Strategies (`strategies/`)
- `vwap_trend.py` — long above / short below VWAP, pullback entries.
- `vwap_mean_reversion.py` — fade at ±1.5σ, exit at VWAP, stop at ±2.5σ, time filter (skip first/last 30 min), volume-pace filter.
- `vwap_breakout_retest.py` — break + retest entry.
- `avwap_regime.py` — anchored at earnings/capitulation low for swing entries.
- Gate `ma_crossover` entries by VWAP side (confluence).

### C. Execution (`execution/`, `brokers/`)
- VWAP execution algo: slice parent order across volume-profile buckets; adaptive to actual volume; participation cap (≤ x% per window).
- Add slippage-vs-VWAP metric (absolute + quadratic) to `utils/result.py`.

### D. Risk (`risk/`)
- Time-of-day filters (no trades first/last 30 min).
- Stop placement at ±2.5σ; max slippage guard (kit's 4 safety checks).
- Volatility–volume interaction check; avoid slicing in low-volume regimes.

### E. Backtesting (`backtests/`)
- Extend `backtest.py` for intraday VWAP with session reset; walk-forward by session.
- Add metrics: VWAP slippage (bps), hit rate, Sharpe, max DD (QuantStats in stack).
- Compare session vs anchored variants.

### F. ML/AI (optional, advanced)
- Dynamic volume allocation via RNN/Transformer (arXiv 2502.18177/2503.02680) — only after rule-based baseline validated.
- Hierarchical RL for parent/child slicing (arXiv 2212.14670).

### G. Web UI (`web/`)
- Chart VWAP + bands + AVWAP anchors; overlay entry/exit markers; show slippage vs VWAP.

## 5. Execution Slicing Math
1. Volume profile from last N days (20): U-shape (~13% first 30 min, ~6% midday, ~12% last 30 min).
2. Allocate: target = bucket_weight × order_size.
3. Adapt: compare actual vs expected cumulative volume per bucket; scale remaining slices up/down.
4. Participation cap: ≤ x% of volume per window.
5. Permanent price impact offset by expected future order flow (SIAM closed-form).
Metrics: absolute VWAP loss (bps), quadratic VWAP loss, R² of volume curve.

## 6. AVWAP Anchor Selection
Anchor candidates: capitulation low, earnings gap open, breakout high, weekly/monthly open.
Critical finding: weekly-anchored VWAP underperformed session VWAP for intraday breakouts (PyQuantLab AAPL). So: intraday → session VWAP; swing/regime → AVWAP with validated anchor per instrument. Anchor only at events with institutional memory.

## 7. Wiring VWAP into Backtest Engine (conceptual)
1. Session state: reset cumulative price×volume and cumulative volume per new day; track current VWAP per bar.
2. SD bands: running std of (price − VWAP) → 1σ/2σ.
3. Time filter: skip signals first/last 30 min.
4. Volume-pace filter: trade only if cumulative session volume ≥ 20-day average pace at that time-of-day.
5. Entry logic: trend = enter on pullback to VWAP while side matches; mean-reversion = enter at ±1.5σ with reversal confirmation; exit at VWAP or ±2.5σ stop.
6. Metrics: add VWAP slippage to `utils/result.py`.
7. Walk-forward by session (VWAP is intraday-only); aggregate session-level PnL.

## 8. Decision Matrix
| Want | Use | Avoid |
|---|---|---|
| Intraday direction bias | Session VWAP trend filter | Anchored VWAP for entries |
| Fade extremes | VWAP ±1.5σ mean reversion | Chasing beyond 2σ without reversal |
| Better fills on large orders | Volume-profile slicing + adaptive | Equal TWAP in U-shaped volume |
| Swing entries | AVWAP at key events | Arbitrary time anchors |
| ML gains | Only after rule-based baseline + walk-forward pass | ML before validation |

## 9. Caveats
- VWAP resets daily — useless multi-day without anchoring.
- Anchored VWAP underperformed session VWAP for intraday breakouts.
- QQQ/TQQQ VWAP trend result (671%/8242%) is leveraged, single-instrument, in-sample-ish — not a guarantee.
- Volume profile is asset- and time-specific — estimate per instrument.
- Deep-learning VWAP gains are execution-cost gains, not alpha.

## 10. Suggested First Step
Validate one simple VWAP trend strategy on one market, intraday 5-min data, with fees, walk-forward, before anything live (kit's "start small").

## Sources
NinjaTrader; SSRN Zarattini & Aziz; QuantifiedStrategies; Schwab; Britannica; Hasbrouck NYU; ScienceDirect; SIAM; arXiv 2502.13722/2502.18177/2503.02680/2212.14670; IEEE M3T; PyQuantLab.

## Related
- [[concepts/scalping-strategies]] — scalping strategies, absorption, OFI, microstructure.
- [[concepts/ml4t-ingest]] — ML4T cost, risk, and monitoring ingestion.