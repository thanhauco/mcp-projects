# MCP-powered Deep Researcher (Local Alternative)

Performs a simple meta-search and extracts readable Markdown from pages for offline summarization.
Tools: `deep_search(query,k)`, `read_url(url)`.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 809
```

