
from common.mcp_core.server import app as base_app
from common.mcp_core.tools import tool
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from doc_ingest import pdf_to_text
import os, uuid

app = base_app
os.makedirs(".chroma_complex", exist_ok=True)
client = PersistentClient(path=".chroma_complex")
coll = client.get_or_create_collection("complex_docs")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

@tool("ingest_pdf")
def ingest_pdf(path: str):
    text = pdf_to_text(path)
    chunks = [text[i:i+800] for i in range(0, len(text), 800)]
    ids = [str(uuid.uuid4()) for _ in chunks]
    embs = embedder.encode(chunks).tolist()
    coll.add(ids=ids, documents=chunks, embeddings=embs)
    return {"ok": True, "chunks": len(chunks)}

@tool("ask")
def ask(query: str, k: int = 3):
    q = embedder.encode([query]).tolist()
    res = coll.query(query_embeddings=q, n_results=k, include=["documents","distances"])
    docs = [{"text": res["documents"][0][i], "score": float(res["distances"][0][i])} for i in range(len(res["documents"][0]))]
    return {"contexts": docs}

@app.get("/health")
def health():
    return {"status":"ok","tools":["ingest_pdf","ask"]}
