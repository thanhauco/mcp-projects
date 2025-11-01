
from common.mcp_core.server import app as base_app
from common.mcp_core.tools import tool
from research import simple_search, fetch_readable

app = base_app

@tool("deep_search")
def deep_search(query: str, k: int = 5):
    return {"results": simple_search(query, num=k)}

@tool("read_url")
def read_url(url: str):
    return fetch_readable(url)

@app.get("/health")
def health():
    return {"status":"ok","tools":["deep_search","read_url"]}
