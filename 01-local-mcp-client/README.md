# 100% Local MCP Client

A minimal local client that discovers and calls tools from a local MCP-like server.
Use this alongside any of the other projects that start a server on port 8000.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 801
```

