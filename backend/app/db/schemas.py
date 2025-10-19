from pydantic import BaseModel
from typing import Optional
from typing import List
import uuid
from datetime import datetime, date


class user(BaseModel):
    username: str
    password: str


class token(BaseModel):
    access_token: str
    token_type: str
    

class menu(BaseModel):
    item_id: Optional[int] = None
    item_name: str
    item_price: float
    

class order(BaseModel):
    order_id: Optional[int] = None
    username: str
    status: str
    
class order_item(BaseModel):
    order_id: int
    item_id: int
    quantity: int
    
class CreateOrderRequest(BaseModel):
    order: order
    items: List[order_item]
    
class CartItemCreate(BaseModel):
    username: str
    item_id: int
    quantity: int = 1


class CartItemRead(BaseModel):
    cart_id: int
    username: str
    item_id: int
    quantity: int