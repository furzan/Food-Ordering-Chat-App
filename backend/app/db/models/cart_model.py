from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .menu_model import Menu


class CartItem(SQLModel, table=True):

    cart_id: Optional[int] = Field(default=None, primary_key=True, index=True)
    username: str = Field(foreign_key="users.username")
    item_id: int = Field(foreign_key="menu.item_id")
    quantity: int = Field(default=1)

    def __repr__(self) -> str:  
        return f"<CartItem {self.cart_id} user={self.username} item_id={self.item_id} qty={self.quantity}>"



