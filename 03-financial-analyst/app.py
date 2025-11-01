
from common.mcp_core.server import app as base_app
from common.mcp_core.tools import tool
import yfinance as yf
import pandas as pd
import pandas_ta as ta

app = base_app

@tool("fetch_ohlc")
def fetch_ohlc(ticker: str = "AAPL", period: str = "6mo", interval: str = "1d"):
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
    return {"rows": min(len(df), 5), "cols": list(df.columns), "sample": df.head(5).reset_index().astype(str).to_dict(orient="records")}

@tool("analyze_trend")
def analyze_trend(ticker: str = "AAPL", period: str = "6mo"):
    df = yf.download(ticker, period=period, interval="1d", auto_adjust=True, progress=False)
    if df.empty:
        return {"error": "No data"}
    df["rsi"] = ta.rsi(df["Close"], length=14)
    df["ema20"] = ta.ema(df["Close"], length=20)
    signal = "neutral"
    if df["Close"].iloc[-1] > df["ema20"].iloc[-1] and df["rsi"].iloc[-1] < 70:
        signal = "bullish"
    elif df["Close"].iloc[-1] < df["ema20"].iloc[-1] and df["rsi"].iloc[-1] > 30:
        signal = "bearish"
    return {"signal": signal, "latest": df.tail(1).reset_index().astype(str).to_dict("records")[0]}

@app.get("/health")
def health():
    return {"status":"ok","tools":["fetch_ohlc","analyze_trend"]}
