from sqlmodel.ext.asyncio.session import AsyncSession
from backend.app.db.models.menu_model import Menu
from backend.app.db.models.order_model import Order
from backend.app.db.models.orderitems_model import OrderItem
from sqlmodel import select, desc
from backend.app.db.schemas import user, order, menu, order_item
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from jose import JWTError, jwt

class order_service:
    
    async def get_menu(self, session: AsyncSession):
        statement = select(Menu)
        result = await session.exec(statement)
        return result.all()
    
    async def create_menu_item(self, item_data: menu, session: AsyncSession):
        item_data_dict = item_data.model_dump()
        new_item = Menu(
            **item_data_dict
        )
        session.add(new_item)
        await session.commit()
        await session.refresh(new_item)
        return new_item
    
    
    
    async def get_order(self, username: str, status: str, session: AsyncSession):
        """Retrieve orders for a username with a specific status.

        Only returns results when status is one of: 'recieved' or 'preparing'.
        Status comparison is case-insensitive.
        """
        allowed = {"recieved", "preparing"}
        if status.lower() not in allowed:
            return []

        statement = select(Order).where(Order.username == username, Order.status == status)
        result = await session.exec(statement)
        return result.all()

    async def create_order(self, order_data: order, items: list[order_item], session: AsyncSession):
        """Create an Order and its OrderItem rows.

        Args:
            order_data: pydantic `order` schema (username, status, optional order_id)
            items: list of pydantic `order_item` schemas (item_id, quantity). The order_id on
                   these items is ignored and set to the created order's id.
            session: AsyncSession

        Returns:
            A dict with the created `order` model instance under 'order' and a list of
            created `OrderItem` model instances under 'items'.
        """
        # create the Order row
        order_dict = order_data.model_dump()
        # remove order_id if provided
        order_dict.pop("order_id", None)

        new_order = Order(**order_dict)
        session.add(new_order)
        await session.commit()
        await session.refresh(new_order)

        created_items = []
        try:
            for it in items:
                it_dict = it.model_dump()
                oi = OrderItem(order_id=new_order.order_id, item_id=it_dict["item_id"], quantity=it_dict["quantity"])
                session.add(oi)
                created_items.append(oi)

            await session.commit()
            # refresh created order items so they contain any defaults from DB
            for oi in created_items:
                await session.refresh(oi)

        except Exception:
            await session.rollback()
            raise

        return {"order": new_order, "items": created_items}
    
    async def get_most_recent_order(self, username: str, session: AsyncSession):
        """Return the most recent Order for a username, or None if not found."""
        statement = select(Order).where(Order.username == username).order_by(desc(Order.order_id)).limit(1)
        result = await session.exec(statement)
        rows = result.all()
        return rows[0] if rows else None
    
    