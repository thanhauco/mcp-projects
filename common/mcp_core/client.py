
from __future__ import annotations
import httpx, json
from .protocol import RPCRequest
from typing import Any, Dict

class MCPClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def list_tools(self):
        r = httpx.get(f"{self.base_url}/tools", timeout=30.0)
        r.raise_for_status()
        return r.json()["tools"]

    def call(self, tool_name: str, **params):
        req = RPCRequest(method=f"tool:{tool_name}", params=params)
        r = httpx.post(f"{self.base_url}/rpc", json=req.model_dump(), timeout=60.0)
        r.raise_for_status()
        data = r.json()
        if data.get("error"):
            raise RuntimeError(data["error"])
        return data["result"]
