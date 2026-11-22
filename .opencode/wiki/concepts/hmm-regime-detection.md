---
title: HMM Regime Detection for Apex Quant
tags: [apex-quant, hmm, regime-detection, research]
sourceRefs:
  - research (web)
lastReviewed: 2026-11-23
---

# HMM Regime Detection for Apex Quant

Implemented: `utils/hmm.py` — GaussianHMM (forward-backward, Viterbi, Baum-Welch with random restarts), `detect_regimes`, `regime_summary`. Tests: `tests/test_hmm.py` (6 tests).

## What it does
- Fits a K-state Gaussian HMM on a return series.
- Decodes most likely state sequence (Viterbi) and posterior probabilities.
- Multi-restart EM to avoid degenerate local optima.

## Usage in Apex Quant
- Regime labels as state variables conditioning other signals (VWAP, z-score, absorption).
- Regime-conditional risk (VaR/CVaR per regime, vol targeting, drawdown limits).
- Feature input to ML extras (optional).

## Caveats
- Assumes Markovian transitions; real markets have long memory and structural breaks.
- State labels are data-driven, not economic labels.
- HMM alone doesn't generate alpha; it conditions existing signals.
- Use AIC/BIC to select state count; 2-3 usually sufficient.