
from common.mcp_core.server import app as base_app
from common.mcp_core.tools import tool
import sqlite3, os

DB_PATH = "voice_agent.db"
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE facts (id INTEGER PRIMARY KEY, topic TEXT, content TEXT)")
    c.executemany("INSERT INTO facts(topic,content) VALUES(?,?)", [
        ("python","Python 3.12 introduced many performance improvements."),
        ("fastapi","FastAPI is a high-performance ASGI framework for Python."),
    ])
    conn.commit()
    conn.close()

app = base_app

@tool("query_db")
def query_db(topic: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content FROM facts WHERE topic = ?", (topic,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"answer": row[0], "mode": "db"}
    return {"answer": "No local fact found. You may fall back to web search.", "mode":"fallback"}

@app.get("/health")
def health():
    return {"status":"ok","tools":["query_db"]}
