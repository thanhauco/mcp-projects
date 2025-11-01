
# MCP Projects Monorepo (9 Projects)

This monorepo contains **nine** MCP-themed projects for AI Engineers. Each project exposes a small set of **tools** via a **local JSON-RPC endpoint** (our minimal "MCP-like" server) and includes an example client / usage.

> Note: This is a pragmatic, local-friendly simulation—**not** the official Model Context Protocol. It lets you wire up agent hosts (Cursor, Claude Desktop, your own scripts) to tools quickly.

## What you get (9 projects)

1. **100% Local MCP Client**  
   A minimal client that discovers and calls tools on any local MCP-like server (runs alone or alongside the others).

2. **MCP-powered Agentic RAG**  
   Local Chroma + Sentence Transformers for embeddings. Falls back to a stub "web search" if similarity is weak.

3. **MCP-powered Financial Analyst**  
   Fetches OHLC with yfinance, computes RSI/EMA via pandas_ta, returns a simple bullish/bearish/neutral signal.

4. **MCP-powered Voice Agent (DB + fallback)**  
   Simple local SQLite knowledge base via `query_db(topic)`; host app can add voice I/O and fall back to web.

5. **Unified MCP Server (DuckDB)**  
   Query multiple local files (CSV/JSON/Parquet) from a single SQL endpoint using DuckDB.

6. **MCP-powered Shared Memory Layer**  
   A shared, local SQLite KV store so Claude Desktop, Cursor, or any host can share context.

7. **MCP-powered RAG over Complex Docs**  
   PDF → text with pdfminer, chunk + embed to Chroma, retrieve top-k contexts with a tool call.

8. **MCP-powered Synthetic Data Generator**  
   Generate realistic tabular data via SDV (CTGAN) using a simple schema.

9. **MCP-powered Deep Researcher (Local Alternative)**  
   Basic DuckDuckGo HTML search + readable Markdown extraction for offline summarization.

## Layout

```
common/mcp_core/      # Lightweight JSON-RPC impl + tool registry + client
01-local-mcp-client/
02-agentic-rag/
03-financial-analyst/
04-voice-agent/
05-unified-server/
06-shared-memory/
07-complex-docs-rag/
08-synthetic-data/
09-deep-researcher/
```

## Visuals (High-Level)

```
  ┌──────────────┐      HTTP JSON-RPC      ┌─────────────────────┐
  │  MCP Host    │ ───────────────────────> │  MCP-like Tool Svc  │
  │ (Cursor/etc) │                          │  (FastAPI server)   │
  └──────────────┘                          └─────────────────────┘
            ▲                                        │
            │                                        │ tool:ingest/search/...
            │                                        ▼
            │                                ┌──────────────────┐
            │                                │ Local Backends   │
            │                                │ (DB, Vector,...) │
            │                                └──────────────────┘
```

### Agentic RAG
```
Query ─> Vector DB (Chroma) ──┐
                              ├─> if low score ⇒ Fallback (stub web search)
Docs ─> Embed & Chunk  ───────┘
```

### Financial Analyst
```
Ticker → yfinance → indicators (EMA/RSI) → signal (bullish/bearish/neutral)
```

### Shared Memory Layer
```
[Claude Desktop] ↔
                  \           ┌───────────────┐
                   \─────────>│ SQLite (KV)  │<─────────/
                  /           └───────────────┘
[Cursor]        ↔
```

## How to run (all projects)

Each project has its own README.md, but they all follow the same pattern:

```bash
cd 02-agentic-rag           # pick a project folder
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
# open http://127.0.0.1:8000/health or POST to /rpc with the JSON-RPC body
```

## How these hang together

The monorepo includes a tiny "MCP-like" core in `common/mcp_core`:

- **server.py** — FastAPI JSON-RPC endpoint (`/rpc`) + `/tools` discovery
- **tools.py** — dead-simple `@tool("name")` decorator & registry
- **client.py** — a lightweight HTTP client for listing/calling tools
- **protocol.py** — minimal JSON-RPC 2.0 request/response models

This is intentionally **not** the official MCP spec — it's a pragmatic local shim so you can wire agents/hosts (Cursor scripts, Claude Desktop, your own app) to local tools quickly and consistently.

## Quick visual

```
MCP Host (Cursor / Claude Desktop / your app)
            │
            │  HTTP JSON-RPC (/rpc)
            ▼
   FastAPI MCP-like Tool Server
            │
            ├── Vector DB (Chroma)
            ├── DuckDB / SQLite
            ├── yfinance / pandas_ta
            └── SDV (synthetic data)
```

Have fun!
