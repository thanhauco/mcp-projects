# MCP-powered Agentic RAG

Embeds documents into a local Chroma DB and performs similarity search; falls back to a stub web-search when no good matches are found.
Expose two tools: `ingest(ids, texts)` and `search(query, threshold)`.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 802
```

