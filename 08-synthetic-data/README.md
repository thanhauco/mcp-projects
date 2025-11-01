# MCP-powered Synthetic Data Generator

Generates realistic tabular synthetic data with SDV using a simple column-type schema.
Tool: `generate_synthetic(schema, rows)`.

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 808
```

