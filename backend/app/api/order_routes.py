from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import StreamingResponse
from backend.app.db.schemas import user, token, menu, order, order_item, CreateOrderRequest, CartItemCreate
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.app.db.main import get_session
from backend.app.services.order_service import order_service

from backend.app.agents.main import agent_stream_generator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel



router = APIRouter()
orderservice = order_service()

@router.get('/menu', status_code= status.HTTP_200_OK)
async def get_menu(session: AsyncSession = Depends(get_session)):
    menu = await orderservice.get_menu(session)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The menu is currently empty. Please check back later."
        )
        
    return menu

@router.post('/menu', status_code= status.HTTP_201_CREATED)
async def create_menu_item(item_data: menu, session: AsyncSession = Depends(get_session)):
    new_item = await orderservice.create_menu_item(item_data, session)
    return new_item




@router.post('/orders', status_code=status.HTTP_201_CREATED)
async def create_order(req: CreateOrderRequest, session: AsyncSession = Depends(get_session)):
    """Create an order and its items using a single request body containing order and items."""
    result = await orderservice.create_order(req.order, req.items, session)
    return result

@router.post('/orders_cart', status_code=status.HTTP_201_CREATED)
async def create_order_from_cart(username: str, session: AsyncSession = Depends(get_session)):
    """Create an order from the user's cart items."""
    result = await orderservice.create_order_from_cart(username, session)
    return result


@router.get('/orders', status_code=status.HTTP_200_OK)
async def get_most_recent_order(username: str, session: AsyncSession = Depends(get_session)):
    """Return the most recent order for the given username (no status filtering)."""
    order_obj = await orderservice.get_most_recent_order(username, session)
    if not order_obj:
        return {}
    return order_obj




@router.get('/cartitems', status_code=status.HTTP_200_OK)
async def get_cart_items(username: str, session: AsyncSession = Depends(get_session)):
    """Return all cart items for the given username."""
    cart_items = await orderservice.get_cart(username, session)
    return cart_items

@router.post('/cartitems', status_code=status.HTTP_201_CREATED)
async def add_cart_item( username: str, cart_items: list[CartItemCreate], session: AsyncSession = Depends(get_session)):
    """Add an item to the cart for the given username."""
    items_as_dicts = [item.model_dump() for item in cart_items]
    new_cart_items = await orderservice.add_to_cart(username= username, items= items_as_dicts, session= session)
    return new_cart_items

@router.put('/cartitems', status_code=status.HTTP_200_OK)
async def updatecart( username: str, cart_item: CartItemCreate, session: AsyncSession = Depends(get_session)):
    """Update an item in the cart for the given username."""
    updated_item = await orderservice.update_cart(username= username, item_id= cart_item.item_id, quantity= cart_item.quantity, session= session)
    return updated_item

@router.delete('/cartitems', status_code=status.HTTP_200_OK)
async def delete_cart( username: str, session: AsyncSession = Depends(get_session)):
    """Delete all cart items for the given username."""
    await orderservice.delete_cart(username= username, session= session)
    return {"detail": "Cart cleared successfully."}


