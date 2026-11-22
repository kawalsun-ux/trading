---
title: Awesome-Quant Insights for Apex Quant
tags: [apex-quant, awesome-quant, microstructure, audit, risk]
sourceRefs:
  - /mnt/c/Users/user/Documents/projects/awesome-quant
lastReviewed: 2026-11-23
---

# Awesome-Quant Insights for Apex Quant

Curated findings from `wilsonfreitas/awesome-quant` relevant to Apex Quant.

## Implemented (zero-dep)
- **VPIN + info-driven bars + trade sign** in `engines/microstructure.py`.
- **PBO + CSCV + MinTRL** in `utils/metrics.py`.
- **Backtest audit toolkit** in `scripts/audit_backtest.py` (ledger conservation, fee double-count, sanity).
- **Limit-order fill simulator** in `execution/fill_simulator.py`.

## Recommended zero-dep additions (future)
- CVaR + Entropy Pooling stress (fortitudo.tech) — extends `risk/`.
- Spread estimators (already in `utils/costs.py`).
- Info-driven bars (volume/dollar/tick) — already in `data/bars.py`.

## Key references
- `orderflow-metrics` (zero-dep microstructure: OFI, VPIN, info-driven bars, Kyle's λ).
- `backtest-audit-kit`, `canli-backtest`, `autonomous-audit` (audit/validation).
- `stochastly-calculators`, `backtester-mcp` (PBO, DSR, CSCV, MinTRL).
- `flashalpha-fill-simulator` (limit-order fill realism).
- `riskkit`, `fortitudo.tech` (risk controls, CVaR stress).
- `hftbacktest` (queue/latency-aware backtesting).

## Backtesting validation checklist (from docs/choosing-backtesting.md)
Lookahead, survivorship, costs & fills, portfolio rules, out-of-sample discipline, reproducibility.