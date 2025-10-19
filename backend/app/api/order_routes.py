from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import StreamingResponse
from backend.app.db.schemas import user, token, menu, order, order_item, CreateOrderRequest
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


@router.get('/orders', status_code=status.HTTP_200_OK)
async def get_most_recent_order(username: str, session: AsyncSession = Depends(get_session)):
    """Return the most recent order for the given username (no status filtering)."""
    order_obj = await orderservice.get_most_recent_order(username, session)
    if not order_obj:
        return {}
    return order_obj



