
from common.mcp_core.server import app as base_app
from common.mcp_core.tools import tool
import sqlite3, os, time

DB = "shared_memory.db"
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS kv(namespace TEXT, k TEXT, v TEXT, ts REAL, PRIMARY KEY(namespace,k))")
conn.commit()
conn.close()

app = base_app

@tool("mem_put")
def mem_put(namespace: str, key: str, value: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO kv(namespace,k,v,ts) VALUES(?,?,?,?)", (namespace, key, value, time.time()))
    conn.commit()
    conn.close()
    return {"ok": True}

@tool("mem_get")
def mem_get(namespace: str, key: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT v, ts FROM kv WHERE namespace=? AND k=?", (namespace, key))
    row = c.fetchone()
    conn.close()
    if not row:
        return {"found": False}
    return {"found": True, "value": row[0], "ts": row[1]}

@tool("mem_list")
def mem_list(namespace: str):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT k, v, ts FROM kv WHERE namespace=?", (namespace,))
    rows = [{"key":k, "value":v, "ts":ts} for (k,v,ts) in c.fetchall()]
    conn.close()
    return {"items": rows}

@app.get("/health")
def health():
    return {"status":"ok","tools":["mem_put","mem_get","mem_list"]}
