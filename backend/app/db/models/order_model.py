from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Order(SQLModel, table=True):
    
    order_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    
    username: str = Field(foreign_key="users.username")
    
    status: str
    
    items: list["OrderItem"] = Relationship(back_populates="order")
    
    user: "Users" = Relationship(back_populates="orders")