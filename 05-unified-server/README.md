# Unified MCP Server (DuckDB)

Query multiple local data sources (CSV/JSON/Parquet) through a single SQL tool.
Tools: `list_sources()`, `query(sql)`.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 805
```

