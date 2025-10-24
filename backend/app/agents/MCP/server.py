# mcp_tools.py
import os
import requests
from typing import Optional, Dict, Any
from mcp.server import FastMCP

mcp = FastMCP("ordering-mcp")

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/api/v1/order")


def _get(path: str, params: Optional[Dict[str, Any]] = None, timeout: float = 10.0):
    url = BACKEND_API_URL.rstrip("/") + "/" + path.lstrip("/")
    r = requests.get(url, params=params or {}, timeout=timeout)
    r.raise_for_status()
    # return JSON if available, else raw text
    try:
        return r.json()
    except ValueError:
        return r.text

def _post(path: str, params: Optional[Dict[str, Any]] = None, payload: Optional[Dict[str, Any]] = None, timeout: float = 10.0):
    url = BACKEND_API_URL.rstrip("/") + "/" + path.lstrip("/")
    r = requests.post(url, params=params or {}, json=payload or {}, timeout=timeout)
    r.raise_for_status()
    try:
        return r.json()
    except ValueError:
        return r.text
    
def _put(path: str, params: Optional[Dict[str, Any]] = None, payload: Optional[Dict[str, Any]] = None, timeout: float = 10.0):
    url = BACKEND_API_URL.rstrip("/") + "/" + path.lstrip("/")
    r = requests.put(url, params=params or {}, json=payload or {}, timeout=timeout)
    r.raise_for_status()
    try:
        return r.json()
    except ValueError:
        return r.text

def _delete(path: str, params: Optional[Dict[str, Any]] = None, timeout: float = 10.0):
    url = BACKEND_API_URL.rstrip("/") + "/" + path.lstrip("/")
    r = requests.delete(url, params=params or {}, timeout=timeout)
    r.raise_for_status()
    try:
        return r.json()
    except ValueError:
        return r.text



@mcp.tool()
def get_menu() -> dict:
    """
        Retrieves the full list of menu items for ordering.

        Returns:
            A list of menu items, each containing:
            {
                "item_id": int,     # Unique item ID
                "item_name": str,   # Dish name
                "item_price": float # Dish price
            }
        """
    return _get("/menu")


@mcp.tool()
def add_to_cart(username: str, cart_items: list[dict]) -> dict:
    """
    Tool: add_to_cart
    Forwards to: POST {BACKEND_API_URL}/cartitems
    Query params:
      username=<username>
    JSON payload:
      [
        {"item_id": <int>, "quantity": <int>},
        {"item_id": <int>, "quantity": <int>},
        ...
      ]
    Returns the backend JSON response.
    """
    params = {"username": username}
    payload = cart_items  # directly forward list of {item_id, quantity}
    return _post("/cartitems", params=params, payload=payload)

@mcp.tool()
def get_cart(username: str) -> dict:
    """
    Tool: get_cart
    Description:
        Retrieves all items currently in the user's shopping cart.

    Query params:
      username=<username>

    Returns:
        The backend JSON response containing the current cart state, typically a list like:
        [
            {'quantity': <int>, 'cart_id': <int>, 'username': <str>, 'item_id': <int>},
            ...
        ]
    """
    params = {"username": username}
    return _get("/cartitems", params=params)


@mcp.tool()
def update_cart(username: str, cart_items: dict) -> dict:
    """
    Tool: update_cart
    Description:
        Updates existing items in the user's cart.
        Use this tool when the user wants to change quantities or remove items.
        in the case of removal, set quantity to 0.

    Query params:
      username=<username>

    JSON payload:
        A list of objects representing updated cart items:
        [
            {"item_id": <int>, "quantity": <int>},  
            ...
        ]

    Returns:
        The updated cart contents as returned by the backend.
    """
    params = {"username": username}
    payload = cart_items
    return _put("/cartitems", params=params, payload=payload)


@mcp.tool()
def delete_cart_item(username: str) -> dict:
    """
    Tool: delete_cart_item
    Description:
        Delete all cart items for the given user.

    Query params:
      username=<username>

    Behavior:
        - Use this tool when the user wants to remove all items completely from their cart.
    """
    params = {"username": username}
    return _delete("/cartitems", params=params)




@mcp.tool()
def create_order_from_cart(username: str) -> dict:
    """
    Tool: create_order_from_cart
    Description:
        Creates a new order using all items currently in the user's cart.

    Query params:
      username=<username>

    Behavior:
        - Transfers all items from the user's cart into a new order.
        - Returns details of the newly created order, including items and total price.

    Returns:
        The backend JSON response with order details, for example:
        {"order": new_order, "items": created_items}
    """
    params = {"username": username}
    return _post("/orders_cart", params=params)

@mcp.tool()
def get_most_recent_order(username: str) -> dict:
    """
    Tool: get_most_recent_order
    Description:
        Retrieves the most recent order placed by the given user.

    Query params:
      username=<username>

    Behavior:
        - Returns details of the latest order (most recent by date).
        - Includes all ordered items and their quantities.
        - If the user has no orders, returns an empty object.

    Returns:
        The backend JSON response, for example:
        {
            "order_id": <int>,
            "username": <str>,
            "total_amount": <float>,
            "items": [
                {"item_name": <str>, "quantity": <int>, "price": <float>},
                {"item_name": <str>, "quantity": <int>, "price": <float>}
            ],
            "status": <str>
        }
    """
    params = {"username": username}
    return _get("/orders", params=params)

@mcp.tool()
def delete_cart_item(username: str, item_id: int) -> dict:
    """
    Tool: delete_cart_item
    Description:
        Deletes a specific item from the user's cart.

    Query params:
      username=<username>
      item_id=<item_id>

    Behavior:
        - Sends a DELETE request to remove a specific cart item for the given username.
        - Returns a confirmation message from the backend.
        - If the item or user is not found, an error message will be returned.

    Returns:
        The backend JSON response, for example:
        {
            "detail": "Cart item 123 deleted successfully."
        }
    """
    params = {"username": username, "item_id": item_id}
    return _delete("/cartitem", params=params)


if __name__ == "__main__":
    mcp.run()
