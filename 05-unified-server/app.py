
from common.mcp_core.server import app as base_app
from common.mcp_core.tools import tool
import duckdb, pandas as pd, os

app = base_app
os.makedirs("data", exist_ok=True)

@tool("list_sources")
def list_sources():
    files = [f for f in os.listdir("data") if f.endswith((".csv",".parquet",".json"))]
    return {"files": files}

@tool("query")
def query(sql: str):
    # Expose DuckDB with access to ./data directory (CSV/JSON/Parquet)
    con = duckdb.connect(database=':memory:')
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("SET home_directory='.';")
    con.execute("SET timezone='UTC';")
    con.execute("CREATE SECRET secret(type 'S3', key_id '', secret '', session_token '');")  # no-op demo
    # DuckDB can read local files with glob patterns
    try:
        df = con.execute(sql).fetchdf()
        return {"rows": len(df), "data": df.head(20).to_dict(orient="records")}
    except Exception as e:
        return {"error": str(e), "hint": "Use DuckDB SQL and reference local files in ./data, e.g., read_csv('data/*.csv')"}

@app.get("/health")
def health():
    return {"status":"ok","tools":["list_sources","query"]}
