
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from common.mcp_core.server import app as base_app
from common.mcp_core.tools import tool
from rag_store import VectorStore

app = base_app
store = VectorStore()

class IndexIn(BaseModel):
    ids: List[str]
    texts: List[str]

@tool("ingest")
def ingest(ids: List[str], texts: List[str]):
    store.add(ids, texts)
    return {"ok": True, "count": len(ids)}

@tool("search")
def search(query: str, threshold: float = 0.4):
    hits = store.query(query, n=3)
    if hits and hits[0][1] < threshold:
        return {"mode": "vector", "hits": hits}
    # fallback to "web search" placeholder
    return {"mode": "fallback", "hits": [{"title":"Fallback search result", "url":"https://example.com"}]}

# Mount simple routes for convenience
@app.get("/health")
def health():
    return {"status":"ok","tools":["ingest","search"]}
