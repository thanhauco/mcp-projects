# MCP-powered Voice Agent (DB + fallback)

A simple local knowledge DB queried via tool `query_db(topic)`. If not found, caller can fall back to web search.
(Voice I/O layer left to the host app; this server focuses on the MCP-like tool.)

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 804
```

