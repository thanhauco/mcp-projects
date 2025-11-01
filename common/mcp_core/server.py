
from __future__ import annotations
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
from .protocol import RPCRequest, RPCResponse
from .tools import call_tool, list_tools

app = FastAPI(title="Local MCP-like Server")

@app.get("/tools")
def get_tools():
    return {"tools": list_tools()}

@app.post("/rpc")
def rpc(req: RPCRequest):
    try:
        if req.method == "list_tools":
            res = {"tools": list_tools()}
        elif req.method.startswith("tool:"):
            tool_name = req.method.split("tool:",1)[1]
            res = call_tool(tool_name, **(req.params or {}))
        else:
            return JSONResponse(RPCResponse(error={"code": -32601, "message": "Method not found"}, id=req.id).model_dump())
        return JSONResponse(RPCResponse(result=res, id=req.id).model_dump())
    except Exception as e:
        return JSONResponse(RPCResponse(error={"code": -32000, "message": str(e)}, id=req.id).model_dump(), status_code=500)
