---
title: Orderflow-Metrics Insights for Apex Quant
tags: [apex-quant, orderflow-metrics, microstructure, volatility, execution]
sourceRefs:
  - /mnt/c/Users/user/Documents/projects/orderflow-metrics
lastReviewed: 2026-11-23
---

# Orderflow-Metrics Insights for Apex Quant

Ingested from `twowaymind/orderflow-metrics` (zero-dep Python/TS microstructure library) into Apex Quant.

## Implemented (zero-dep, stdlib)
- **Multi-level OFI (mlofi)**, weighted mid (micro-price), relative spread bps, OFI contribution, order-flow entropy in `engines/microstructure.py`.
- **Realized volatility suite** in `utils/volatility.py`: realized var/vol/skew/kurt, annualized; range-based (Parkinson, Garman-Klass, Rogers-Satchell, Yang-Zhang); jump-robust (bipower, MinRV, MedRV, realized quarticity, relative jump); HAR-RV forecast.
- **TCA** in `execution/tca.py`: effective/realized spread, price impact, implementation shortfall, Kyle's lambda.
- **Execution scheduling** in `execution/scheduling.py`: TWAP, POV.
- **Online streaming estimators** in `utils/online.py`: Welford, EWMA, EWMA variance, rolling window.
- **Mean-reversion / OU** in `utils/meanrev.py`: speed, half-life, z-score.
- **Realized covariance/correlation/beta** in `utils/covariance.py`.

## Key references
- Cont-Kukanov-Stoikov OFI; Cont-Cucuringu-Zhang multi-level OFI.
- Parkinson, Garman-Klass, Rogers-Satchell, Yang-Zhang range vol.
- Barndorff-Nielsen-Shephard bipower/MinRV/MedRV.
- Corsi HAR-RV.
- Pastor-Stambaugh liquidity (future).
- Amaya et al. realized skewness/kurtosis.

## Tests
- `tests/test_phase10.py` (27 tests) covering all new modules.
- Zero-dep sweep clean.