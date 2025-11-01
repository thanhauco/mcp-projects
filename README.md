
# MCP Projects Monorepo (9 Projects)

This monorepo contains **nine** MCP-themed projects for AI Engineers. Each project exposes a small set of **tools** via a **local JSON-RPC endpoint** (our minimal "MCP-like" server) and includes an example client / usage.

> Note: This is a pragmatic, local-friendly simulation—**not** the official Model Context Protocol. It lets you wire up agent hosts (Cursor, Claude Desktop, your own scripts) to tools quickly.

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

## How to Run Any Project

1. `cd 0X-project-name`
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `uvicorn app:app --reload --port 8000`  (or project-specific port in README)
5. From another terminal, the client (example: Project 01) can call `GET /tools` or `/rpc`.

Have fun!
