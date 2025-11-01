
from __future__ import annotations
from typing import Callable, Dict, Any
from pydantic import BaseModel, Field

_TOOL_REGISTRY: Dict[str, Callable[..., Any]] = {}

def tool(name: str):
    """Decorator to register a function as a tool with a given name."""
    def wrap(fn: Callable[..., Any]):
        _TOOL_REGISTRY[name] = fn
        return fn
    return wrap

def list_tools():
    return list(_TOOL_REGISTRY.keys())

def call_tool(name: str, **kwargs):
    if name not in _TOOL_REGISTRY:
        raise KeyError(f"Tool '{name}' not found")
    return _TOOL_REGISTRY[name](**kwargs)
