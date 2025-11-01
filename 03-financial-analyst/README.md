# MCP-powered Financial Analyst

Fetches market data with yfinance, computes RSI/EMA, and returns a simple sentiment signal via tools `fetch_ohlc` and `analyze_trend`.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 803
```

