# 10. MCP-powered Evals + Telemetry

A telemetry and evaluation server that logs every tool call, measures latency, and exposes Prometheus metrics with a simple dashboard.

## Features

- **Tool Call Logging**: Logs every tool invocation with timestamp, parameters, and results
- **Latency Tracking**: Measures execution time for each tool call
- **Prometheus Metrics**: Exposes metrics endpoint for monitoring
- **Simple Dashboard**: Built-in web UI to view metrics and logs
- **SQLite Storage**: Persistent storage for historical data

## Metrics Tracked

- Total tool calls (counter)
- Tool call latency (histogram)
- Tool call errors (counter)
- Active tool calls (gauge)

## Setup

```bash
cd 10-evals-telemetry
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app:app --reload --port 8010
```

## Endpoints

- `GET /health` - Health check
- `GET /tools` - List available tools
- `POST /rpc` - JSON-RPC endpoint
- `GET /metrics` - Prometheus metrics
- `GET /dashboard` - Web dashboard
- `GET /logs` - Recent tool call logs (JSON)

## Tools

1. **log_event** - Manually log a custom event
2. **get_stats** - Get aggregated statistics
3. **clear_logs** - Clear old logs (optional retention period)

## Example Usage

```python
# Log a custom event
{
  "jsonrpc": "2.0",
  "method": "log_event",
  "params": {
    "event_type": "user_action",
    "data": {"action": "button_click", "user_id": "123"}
  },
  "id": 1
}

# Get statistics
{
  "jsonrpc": "2.0",
  "method": "get_stats",
  "params": {"hours": 24},
  "id": 2
}
```

## Dashboard

Open `http://127.0.0.1:8010/dashboard` to view:
- Real-time metrics
- Recent tool calls
- Latency distribution
- Error rates

## Integration

This server can be used alongside other MCP projects to monitor their tool usage:

```python
from common.mcp_core.client import MCPClient

# Your main tool server
main_client = MCPClient("http://localhost:8000")

# Telemetry server
telemetry = MCPClient("http://localhost:8010")

# Wrap calls with telemetry
result = main_client.call_tool("search", {"query": "test"})
telemetry.call_tool("log_event", {
    "event_type": "tool_call",
    "data": {"tool": "search", "success": True}
})
```
