"""Market data helpers."""
import yfinance as yf
import pandas as pd
from pathlib import Path

CACHE = Path(__file__).resolve().parents[1] / "data" / "cache"

def load_ohlcv(ticker: str, start="2018-01-01", end=None, interval="1d") -> pd.DataFrame:
    cache_file = CACHE / f"{ticker}_{interval}.csv"
    if cache_file.exists():
        df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
        if end is None or df.index.max().strftime("%Y-%m-%d") >= (end or "9999"):
            return df
    df = yf.download(ticker, start=start, end=end, interval=interval, auto_adjust=True, progress=False)
    df = df.dropna()
    CACHE.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache_file)
    return df

def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ret"] = df["Close"].pct_change()
    df["logret"] = (df["Close"] / df["Close"].shift(1)).apply(lambda x: __import__("numpy").log(x) if x and x > 0 else float("nan"))
    return df