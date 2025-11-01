
"""
A tiny JSON-RPC 2.0 implementation to simulate MCP-style tool calls over HTTP.
This isn't the official MCP, but a minimal local protocol to help you prototype.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Callable
import uuid

JSON = Dict[str, Any]

class RPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class RPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
