from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from typing import Optional 

class Menu(SQLModel, table=True):
    item_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    item_name: str
    item_price: float
    
    order_items: list["OrderItem"] = Relationship(back_populates="menu_item")

