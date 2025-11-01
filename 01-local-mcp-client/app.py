
from fastapi import FastAPI
from common.mcp_core.client import MCPClient

app = FastAPI(title="100% Local MCP Client Demo")
client = MCPClient(base_url="http://127.0.0.1:8000")  # Point to any local MCP-like server

@app.get("/demo")
def demo():
    try:
        tools = client.list_tools()
        result = {"tools": tools}
        if tools:
            # Call the first tool with no params as a demo
            try:
                out = client.call(tools[0])
                result["sample_call"] = {tools[0]: out}
            except Exception as e:
                result["sample_call_error"] = str(e)
        return result
    except Exception as e:
        return {"error": str(e), "hint": "Make sure a local server from other projects is running on :8000"}
