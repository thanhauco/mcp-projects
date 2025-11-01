# MCP-powered RAG over Complex Docs

Parses PDFs to text (via pdfminer), chunks & embeds to Chroma, and answers queries by retrieving top-k contexts.
Tools: `ingest_pdf(path)`, `ask(query,k)`.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 807
```

