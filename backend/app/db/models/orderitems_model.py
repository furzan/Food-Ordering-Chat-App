from sqlmodel import Field, SQLModel, Relationship

class OrderItem(SQLModel, table=True):
    order_id: int = Field(foreign_key="order.order_id", primary_key=True)
    
    item_id: int = Field(foreign_key="menu.item_id", primary_key=True)

    order: "Order" = Relationship(back_populates="items")
    
    menu_item: "Menu" = Relationship(back_populates="order_items")