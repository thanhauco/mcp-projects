# MCP-powered Shared Memory Layer

Cross-operate between tools/hosts by storing and retrieving context in a shared local SQLite DB.
Tools: `mem_put(namespace,key,value)`, `mem_get(namespace,key)`, `mem_list(namespace)`.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 806
```

