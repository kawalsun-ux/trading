---
title: ML4T Ingestion into Apex Quant
tags: [apex-quant, ml4t, ingest, research]
sourceRefs:
  - /mnt/c/Users/user/Documents/projects/machine-learning-for-trading
lastReviewed: 2026-11-23
---

# ML4T Ingestion into Apex Quant

Ingested from `stefan-jansen/machine-learning-for-trading` (3rd ed.) into Apex Quant, zero-dep (stdlib only).

## Implemented (Phases 0–1, 2, 4, 5, 7 partial)
- **Phase 0 baseline:** `tests/test_backtest_parity.py`, `scripts/check_backtest_parity.py`, `utils/runlog.py`, `docs/backtest_protocol.md`.
- **Phase 1 costs:** `utils/costs.py` (Corwin-Schultz, Roll, Kyle λ, sqrt impact, cost stack, gross-vs-net, cost cliff); `engines/backtest.py` now supports `cost_model` (flat/spread/impact/dynamic) via `_slip_for`.
- **Phase 2 bars:** `data/bars.py` (volume/dollar/tick bars, sessionize); `engines/microstructure.py` additions (spread_proxy, volume_profile, regime_tag).
- **Phase 4 risk:** `risk/tail.py`, `risk/drawdown.py`, `risk/factor.py`, `risk/stress.py`, `risk/adaptive.py`.
- **Phase 5 metrics:** `utils/metrics.py` (deflated Sharpe, Sharpe CI, Rademacher).
- **Phase 7 monitoring:** `monitoring/drift.py` (PSI, KS, rolling mean), `monitoring/circuit_breakers.py`.

## Pending
- Phase 3 features (`utils/features.py`: point-in-time align, calendar encoding, feature spec).
- Phase 6 live readiness (`execution/state_machine.py`, parity, safety).
- Phase 8 research process (strategy map, trading setup templates, search accounting).
- Heavy ML (xgboost, optuna, shap, stable-baselines3) — optional `extras/` only.

## Zero-dep compliance
All new core modules stdlib only. `monitoring` added to `APP_DIRS` in `tests/test_zero_dependency.py`. 41 tests pass; hygiene clean.

## Related
- [[concepts/vwap-strategies]] — VWAP execution and slicing research.
- [[concepts/scalping-strategies]] — scalping research and roadmap.

## Key references
- Ch. 18 transaction costs (cost taxonomy, spread estimation, market impact, VWAP/TWAP, Almgren-Chriss, gross-vs-net, cost cliff).
- Ch. 3 microstructure (LOB, intraday patterns, bar types, sessionization).
- Ch. 8 feature engineering (horizon alignment, point-in-time, one-knob-at-a-time).
- Ch. 19 risk (VaR/CVaR, drawdowns, factor exposure, stress, adaptive controls, kill switches).
- Ch. 16 simulation (protocol, DSR, search-aware inference).
- Ch. 25 live trading (unified framework, order state machine, parity, staged rollout).
- Ch. 26 MLOps (drift, circuit breakers, safe model updates).