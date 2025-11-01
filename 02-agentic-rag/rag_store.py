
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

class VectorStore:
    def __init__(self, collection_name: str = "docs"):
        self.client = chromadb.PersistentClient(path=".chroma")
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def add(self, ids: List[str], texts: List[str], metadatas=None):
        embs = self.embedder.encode(texts).tolist()
        self.collection.add(ids=ids, documents=texts, embeddings=embs, metadatas=metadatas)

    def query(self, text: str, n: int = 3) -> List[Tuple[str,float]]:
        q = self.embedder.encode([text]).tolist()
        res = self.collection.query(query_embeddings=q, n_results=n, include=["embeddings","documents","metadatas", "distances"])
        out = []
        if res["ids"]:
            for i,doc_id in enumerate(res["ids"][0]):
                dist = res["distances"][0][i]
                out.append((doc_id, float(dist)))
        return out
