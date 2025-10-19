# mcp_tools.py
import os
import requests
from typing import Optional, Dict, Any
from mcp.server import FastMCP

mcp = FastMCP("ordering-mcp")

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")


def _get(path: str, params: Optional[Dict[str, Any]] = None, timeout: float = 10.0):
    url = BACKEND_API_URL.rstrip("/") + "/" + path.lstrip("/")
    r = requests.get(url, params=params or {}, timeout=timeout)
    r.raise_for_status()
    # return JSON if available, else raw text
    try:
        return r.json()
    except ValueError:
        return r.text

def _post(path: str, payload: Optional[Dict[str, Any]] = None, timeout: float = 10.0):
    url = BACKEND_API_URL.rstrip("/") + "/" + path.lstrip("/")
    r = requests.post(url, json=payload or {}, timeout=timeout)
    r.raise_for_status()
    try:
        return r.json()
    except ValueError:
        return r.text


@mcp.tool()
def get_menu(category: Optional[str] = None, query: Optional[str] = None, page: Optional[int] = None) -> dict:
    """
    Tool: get_menu
    Forwards to: GET {BACKEND_API_URL}/menu
    Params:
      - category (optional)
      - query (optional) - search term
      - page (optional) - pagination
    Returns the backend JSON response.
    """
    params = {}
    if category:
        params["category"] = category
    if query:
        params["q"] = query
    if page is not None:
        params["page"] = page
    return _get("/menu", params=params)


@mcp.tool()
def add_to_cart(session_id: str, item_id: str, qty: int = 1, modifiers: Optional[Dict[str, Any]] = None) -> dict:
    """
    Tool: add_to_cart
    Forwards to: POST {BACKEND_API_URL}/cart
    Payload forwarded as JSON:
      {
        "session_id": "...",
        "item_id": "...",
        "qty": 1,
        "modifiers": {...}  # optional
      }
    Returns the backend JSON response.
    """
    payload = {
        "session_id": session_id,
        "item_id": item_id,
        "qty": qty,
    }
    if modifiers is not None:
        payload["modifiers"] = modifiers
    return _post("/cart", payload=payload)


@mcp.tool()
def place_order(session_id: str, payment_token: Optional[str] = None, address: Optional[Dict[str, Any]] = None, notes: Optional[str] = None) -> dict:
    """
    Tool: place_order
    Forwards to: POST {BACKEND_API_URL}/order
    Payload example:
      {
        "session_id": "...",
        "payment_token": "...",   # optional
        "address": { ... },       # optional
        "notes": "..."
      }
    Returns the backend JSON response (should include order_id / status).
    """
    payload = {"session_id": session_id}
    if payment_token is not None:
        payload["payment_token"] = payment_token
    if address is not None:
        payload["address"] = address
    if notes is not None:
        payload["notes"] = notes
    return _post("/order", payload=payload)


@mcp.tool()
def get_order_status(order_id: str) -> dict:
    """
    Tool: get_order_status
    Forwards to: GET {BACKEND_API_URL}/orders/{order_id}
    Returns the backend JSON response.
    """
    path = f"/orders/{order_id}"
    return _get(path)


if __name__ == "__main__":
    # run the MCP server; change host/port if needed
    # example: mcp.run(host="0.0.0.0", port=9000)
    mcp.run()
