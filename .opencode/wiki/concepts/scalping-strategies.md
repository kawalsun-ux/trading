---
title: Scalping Strategies Research for Apex Quant
tags: [trading, scalping, microstructure, research, apex-quant]
sourceRefs:
  - https://jonathankinlay.com/2019/10/high-frequency-scalping-strategies
  - https://quantstrategy.io/blog/scalping-strategies-how-to-use-order-book-imbalance-and/
  - https://quantstrategy.io/blog/backtesting-order-flow-strategies-metrics-and-pitfalls-to/
  - https://arxiv.org/html/2502.18625v1
  - https://blog.quantlogicx.com/blog/advanced-scalping-strategy-types-2026-traders-guide
  - https://tradingedgejournal.com/blog/do-liquidity-sweeps-work/
lastReviewed: 2026-11-22
---

# Scalping Strategies Research for Apex Quant

Research-only (no code in this page; implementations noted below).

## 0. Scalping Reality
- Costs dominate at 1-3 tick targets; dynamic slippage modeling mandatory.
- Fill rates ~22% on volume bars; 25% acceptable, 10-15% ideal (Kinlay).
- Naive market making / raw OFI unprofitable after fees (arXiv 2502.18625).
- Latency: order book signals decay in seconds.

## 1. Strategy Options Ranked
A. VWAP Deviation Scalping — reuse engines/vwap.py + vwap_bands/vwap_mean_reversion. High retail feasibility.
B. OFI with Counter-Signal — engines/microstructure.py has ofi_state; needs L2 + low latency. Medium.
C. Absorption / Liquidity Sweep Reversal — tick data ideal; 1-min + volume spikes OK. Medium-High.
D. Micro-Momentum / Breakout — L2; best 9:30-10:30 ET. Medium.
E. Intraday Mean Reversion (z-score) — utils/indicators.zscore. High.
F. Market Making / Spread Capture — poor for retail; avoid naive.
G. Spread Scalping — avoid (negative expectancy retail).

## 2. Apex Quant Existing Infra
engines/microstructure.py (OFI, depth, normalize, fit_slope, ofi_state); engines/vwap.py; engines/signals.py (vwap_*, book_imbalance stub, mean_reversion); engines/indicators.py (sma, ema, atr, rsi, vwap_series, zscore); engines/backtest.py; risk/, brokers/, utils/result.py.

## 3. Roadmap (implemented 2026-11-22)
Phase 1 (done):
- vwap_trend, vwap_mean_reversion signals (engines/signals.py)
- zscore_reversion signal (intraday mean reversion, time filter)
- absorption signal (high-volume flat bar reversal)
- utils/result.py helpers: deviation_bps, vwap_slippage_bps, time_of_day_minutes, in_session_window

Phase 2 (pending): intraday data upgrade, dynamic slippage model in backtest, fill-rate modeling.
Phase 3 (pending): complete book_imbalance with spoofing filter; absorption detector polish; time-of-day gating (9:30-10:30 ET).
Phase 4 (pending): OFI counter-signal; adaptive market making.

## 4. Universal Scalping Rules
- Risk 0.1-0.25%/trade; hard stops 1-3 ticks.
- Exit on book flip or >50% retracement.
- Disable midday low-volume.
- Validate with random-entry control + dynamic costs.
- Latency budget explicit; else fall back to 5-min VWAP.

## 5. Do Not
- Naive market making / spread scalping on retail fees.
- Raw OFI as standalone alpha.
- Assume 100% fill rates.
- Liquidity sweeps with tight stops.

## Sources
Kinlay; QuantStrategy.io; QuantLogicX; arXiv 2502.18625; Cont et al. OFI; Dean Markwick; Quantt; TradingEdge Journal; CFA HFT; Ceti̇n.

## Related
- [[concepts/vwap-strategies]] — VWAP/AVWAP strategies and execution slicing.