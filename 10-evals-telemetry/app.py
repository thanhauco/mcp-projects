"""
MCP-powered Evals + Telemetry Server
Logs tool calls, tracks latency, exposes Prometheus metrics + dashboard
"""
import sys
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Add common to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from common.mcp_core.server import MCPServer
from common.mcp_core.tools import tool

# Initialize FastAPI + MCP
app = FastAPI(title="MCP Evals + Telemetry")
mcp = MCPServer()

# Database setup
DB_PATH = Path(__file__).parent / "telemetry.db"

# Prometheus metrics
tool_calls_total = Counter('mcp_tool_calls_total', 'Total tool calls', ['tool_name', 'status'])
tool_call_duration = Histogram('mcp_tool_call_duration_seconds', 'Tool call duration', ['tool_name'])
tool_calls_active = Gauge('mcp_tool_calls_active', 'Active tool calls')
tool_errors_total = Counter('mcp_tool_errors_total', 'Total tool errors', ['tool_name', 'error_type'])


def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tool_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            params TEXT,
            result TEXT,
            duration_ms REAL,
            status TEXT,
            error TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            data TEXT
        )
    """)
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def log_tool_call(tool_name: str, params: Any, result: Any, duration_ms: float, 
                  status: str, error: Optional[str] = None):
    """Log a tool call to database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tool_calls (timestamp, tool_name, params, result, duration_ms, status, error)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            tool_name,
            str(params),
            str(result)[:1000],  # Truncate long results
            duration_ms,
            status,
            error
        ))
        conn.commit()


# Tools
@tool("log_event")
def log_event(event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log a custom event
    
    Args:
        event_type: Type of event (e.g., 'user_action', 'system_event')
        data: Event data as dictionary
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO events (timestamp, event_type, data)
            VALUES (?, ?, ?)
        """, (datetime.utcnow().isoformat(), event_type, str(data)))
        conn.commit()
    
    return {
        "status": "logged",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat()
    }


@tool("get_stats")
def get_stats(hours: int = 24) -> Dict[str, Any]:
    """
    Get aggregated statistics for the specified time period
    
    Args:
        hours: Number of hours to look back (default: 24)
    """
    cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total calls
        cursor.execute("""
            SELECT COUNT(*) as total, 
                   AVG(duration_ms) as avg_duration,
                   MIN(duration_ms) as min_duration,
                   MAX(duration_ms) as max_duration
            FROM tool_calls 
            WHERE timestamp > ?
        """, (cutoff,))
        overall = dict(cursor.fetchone())
        
        # By tool
        cursor.execute("""
            SELECT tool_name, 
                   COUNT(*) as calls,
                   AVG(duration_ms) as avg_duration,
                   SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors
            FROM tool_calls 
            WHERE timestamp > ?
            GROUP BY tool_name
            ORDER BY calls DESC
        """, (cutoff,))
        by_tool = [dict(row) for row in cursor.fetchall()]
        
        # Recent events
        cursor.execute("""
            SELECT event_type, COUNT(*) as count
            FROM events
            WHERE timestamp > ?
            GROUP BY event_type
        """, (cutoff,))
        events = [dict(row) for row in cursor.fetchall()]
    
    return {
        "period_hours": hours,
        "overall": overall,
        "by_tool": by_tool,
        "events": events
    }


@tool("clear_logs")
def clear_logs(days: int = 30) -> Dict[str, Any]:
    """
    Clear logs older than specified days
    
    Args:
        days: Keep logs from last N days (default: 30)
    """
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tool_calls WHERE timestamp < ?", (cutoff,))
        calls_deleted = cursor.rowcount
        cursor.execute("DELETE FROM events WHERE timestamp < ?", (cutoff,))
        events_deleted = cursor.rowcount
        conn.commit()
    
    return {
        "status": "cleared",
        "tool_calls_deleted": calls_deleted,
        "events_deleted": events_deleted,
        "kept_days": days
    }


# Middleware to track all tool calls
@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    """Track metrics for all requests"""
    if request.url.path == "/rpc":
        tool_calls_active.inc()
        start_time = time.time()
        
        # Get request body for tool name
        body = await request.body()
        tool_name = "unknown"
        try:
            import json
            data = json.loads(body)
            tool_name = data.get("method", "unknown")
        except:
            pass
        
        # Restore body for downstream
        async def receive():
            return {"type": "http.request", "body": body}
        request._receive = receive
        
        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000
            
            # Update metrics
            tool_call_duration.labels(tool_name=tool_name).observe(time.time() - start_time)
            tool_calls_total.labels(tool_name=tool_name, status="success").inc()
            
            # Log to database
            log_tool_call(tool_name, {}, "success", duration, "success")
            
            return response
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            tool_calls_total.labels(tool_name=tool_name, status="error").inc()
            tool_errors_total.labels(tool_name=tool_name, error_type=type(e).__name__).inc()
            log_tool_call(tool_name, {}, None, duration, "error", str(e))
            raise
        finally:
            tool_calls_active.dec()
    else:
        response = await call_next(request)
        return response


# Routes
@app.get("/health")
def health():
    return {"status": "healthy", "service": "mcp-evals-telemetry"}


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/logs")
def get_logs(limit: int = 100):
    """Get recent tool call logs"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM tool_calls 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        logs = [dict(row) for row in cursor.fetchall()]
    return {"logs": logs, "count": len(logs)}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """Simple dashboard UI"""
    stats = get_stats(hours=24)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MCP Telemetry Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .card {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #333; }}
            h2 {{ color: #666; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #f8f8f8; font-weight: bold; }}
            .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
            .metric-label {{ font-size: 12px; color: #666; }}
        </style>
        <script>
            setInterval(() => location.reload(), 30000); // Refresh every 30s
        </script>
    </head>
    <body>
        <div class="container">
            <h1>🔍 MCP Telemetry Dashboard</h1>
            
            <div class="card">
                <h2>Overall Stats (Last 24h)</h2>
                <div class="metric">
                    <div class="metric-value">{stats['overall']['total'] or 0}</div>
                    <div class="metric-label">Total Calls</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{stats['overall']['avg_duration'] or 0:.2f}ms</div>
                    <div class="metric-label">Avg Duration</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{stats['overall']['min_duration'] or 0:.2f}ms</div>
                    <div class="metric-label">Min Duration</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{stats['overall']['max_duration'] or 0:.2f}ms</div>
                    <div class="metric-label">Max Duration</div>
                </div>
            </div>
            
            <div class="card">
                <h2>By Tool</h2>
                <table>
                    <tr>
                        <th>Tool Name</th>
                        <th>Calls</th>
                        <th>Avg Duration</th>
                        <th>Errors</th>
                    </tr>
                    {''.join(f'''
                    <tr>
                        <td>{tool['tool_name']}</td>
                        <td>{tool['calls']}</td>
                        <td>{tool['avg_duration']:.2f}ms</td>
                        <td>{tool['errors']}</td>
                    </tr>
                    ''' for tool in stats['by_tool'])}
                </table>
            </div>
            
            <div class="card">
                <h2>Events</h2>
                <table>
                    <tr>
                        <th>Event Type</th>
                        <th>Count</th>
                    </tr>
                    {''.join(f'''
                    <tr>
                        <td>{event['event_type']}</td>
                        <td>{event['count']}</td>
                    </tr>
                    ''' for event in stats['events'])}
                </table>
            </div>
            
            <div class="card">
                <h2>Endpoints</h2>
                <ul>
                    <li><a href="/metrics">/metrics</a> - Prometheus metrics</li>
                    <li><a href="/logs">/logs</a> - Recent logs (JSON)</li>
                    <li><a href="/tools">/tools</a> - Available tools</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    return html


# Mount MCP routes
app.mount("/", mcp.app)


# Initialize database on startup
@app.on_event("startup")
def startup():
    init_db()
    print("✅ Telemetry database initialized")
    print("📊 Dashboard: http://127.0.0.1:8010/dashboard")
    print("📈 Metrics: http://127.0.0.1:8010/metrics")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8010)
