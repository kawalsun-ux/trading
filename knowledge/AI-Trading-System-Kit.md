# AI Trading System Kit (from PDF)

Source: `AI-Trading-System-Kit.pdf` (desktop). Educational only. Not financial advice.

## How the 7 fit together
1. Connect: Solana.py (connector to Solana accounts, token data, transactions)
2. Trade: Raydium SDK V2 (pool reader, builds swaps) + Orca Whirlpools (second exchange)
3. Test: VectorBT (backtester, fees, drawdowns)
4. Record: DuckDB (market snapshots, trade records) + QuantStats (performance reports)
5. See: Lightweight Charts (live dashboard)

## Claude setup prompt (paste into Claude Code)
"Help me build a small trading research system using these 7 GitHub repos: [paste links].
Install each one, explain what it does in plain English, and connect them step by step.
Before any trade is sent, check the token, my available balance, how fresh the price
quote is, and the maximum slippage. Save every confirmed transaction before updating
my position. Start in test mode only, with no real money.
Read what Claude plans to install before you approve it."

## The 4 safety checks before any trade is signed
1. Right token — not a copycat with the same name.
2. Enough balance — the funds are actually there.
3. Fresh quote — the price isn't stale.
4. Max slippage — the price can't run away from you.
Then: sign only if all 4 pass, record the confirmed trade, and only then update position.

## Repos
1. Solana.py — connector. github.com/michaelhly/solana-py (MIT, ~1.4k stars, Python)
2. Raydium SDK V2 — pool reader. github.com/raydium-io/raydium-sdk-V2 (GPL-3.0, ~349 stars, TS)
3. Orca Whirlpools — second exchange. github.com/orca-so/whirlpools (~540 stars)
4. VectorBT — backtester. github.com/polakowo/vectorbt (Apache-2.0 + Commons Clause, ~9.6k stars, Python)
5. DuckDB — memory/store. github.com/duckdb/duckdb (MIT, ~41.1k stars)
6. QuantStats — report card. github.com/ranaroussi/quantstats (Apache-2.0, ~7.5k stars, Python)
7. Lightweight Charts — dashboard. github.com/tradingview/lightweight-charts (Apache-2.0, ~17.2k stars, TS)

## Per-repo setup highlights
- Solana.py: read one wallet balance as first test, no trading.
- Raydium: fetch one pool's price; never sign a swap until safety checks in place.
- Orca: compare one token's price on Raydium and Orca; pick best quote, not trade more.
- VectorBT: test one simple rule on past data with fees; if it fails, don't try real money.
- DuckDB: create trade log table; save every signal, rejection, filled trade; replay a day.
- QuantStats: feed backtest/paper results; read losing periods as closely as wins.
- Lightweight Charts: build simple web page with one chart; plot prices + entry/exit markers.

## Start small
1. One market only.
2. Replay full workflow on past data.
3. Test mode with no money until every decision makes sense.
4. System should explain a rejected trade as clearly as a filled one.

## Warnings
New Solana tokens are extremely risky and many go to zero. Free open-source tools: check each repo for latest install steps. Never connect real money until you understand what the system does. Educational only. Not financial advice. Trading involves risk of loss.
"""