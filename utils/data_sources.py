"""Additional market data sources."""
import os
import pandas as pd
import yfinance as yf
import ccxt
from pathlib import Path

CACHE = Path(__file__).resolve().parents[1] / "data" / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

def equities(tickers, start="2018-01-01", end=None, interval="1d"):
    df = yf.download(tickers, start=start, end=end, interval=interval,
                     auto_adjust=True, progress=False, group_by="ticker")
    return df

def crypto_ohlcv(symbol="BTC/USDT", exchange="binance", timeframe="1d",
                 limit=1000, since=None):
    ex = getattr(ccxt, exchange)({"enableRateLimit": True})
    ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "Open", "High", "Low", "Close", "Volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.set_index("timestamp")
    return df

def forex(pair="EURUSD=X", start="2018-01-01", end=None):
    return yf.download(pair, start=start, end=end, auto_adjust=True, progress=False)

def macro(series="GDP", source="fred", start="2000-01-01"):
    try:
        import pandas_datareader as pdr
        return pdr.get_data_fred(series, start)
    except Exception as e:
        print("macro fetch failed:", e)
        return pd.DataFrame()

def from_csv(path, date_col="Date"):
    df = pd.read_csv(path)
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.set_index(date_col)
    return df