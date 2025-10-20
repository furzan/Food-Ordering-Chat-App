from sqlmodel.ext.asyncio.session import AsyncSession
from backend.app.db.models.menu_model import Menu
from backend.app.db.models.order_model import Order
from backend.app.db.models.orderitems_model import OrderItem
from backend.app.db.models.cart_model import CartItem
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

        allowed = {"recieved", "preparing"}
        if status.lower() not in allowed:
            return []

        statement = select(Order).where(Order.username == username, Order.status == status)
        result = await session.exec(statement)
        return result.all()

    async def create_order(self, order_data: order, items: list[order_item], session: AsyncSession):

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
    
    async def create_order_from_cart(self, username: str, session: AsyncSession):
        """Create an Order from the user's cart, create OrderItems, and clear the cart.

        Returns a dict with 'order' and 'items'.
        """
        # load cart items
        stmt = select(CartItem).where(CartItem.username == username)
        result = await session.exec(stmt)
        cart_rows = result.all()
        if not cart_rows:
            raise ValueError("cart is empty")

        # build order data
        new_order = Order(username=username, status="recieved")
        session.add(new_order)
        await session.commit()
        await session.refresh(new_order)

        created_items = []
        try:
            for c in cart_rows:
                oi = OrderItem(order_id=new_order.order_id, item_id=c.item_id, quantity=c.quantity)
                session.add(oi)
                created_items.append(oi)

            await session.commit()

            for oi in created_items:
                await session.refresh(oi)

            # clear cart for user
            for c in cart_rows:
                await session.delete(c)
            await session.commit()

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
    
    
    
    
    
    async def get_cart(self, username: str, session: AsyncSession):
        """Retrieve the current cart for a user."""
        statement = select(CartItem).where(CartItem.username == username)
        result = await session.exec(statement)
        rows = result.all()
        return rows if rows else None

    async def add_to_cart(self, username: str, item_id: int = None, quantity: int = 1, items: list = None, session: AsyncSession = None):
        """Add one or more items to the user's cart.

        Usage:
        - Single item: provide `item_id` and optional `quantity` (default 1).
        - Multiple items: provide `items` as a list where each entry is either
          a dict {'item_id': int, 'quantity': int} or a tuple (item_id, quantity).

        Returns a list of CartItem rows that were created/updated.
        """
        if session is None:
            raise ValueError("session is required")

        to_process = []
        # prefer items list if provided
        if items:
            for ent in items:
                if isinstance(ent, dict):
                    iid = ent.get("item_id")
                    qty = ent.get("quantity", 1)
                elif isinstance(ent, (list, tuple)):
                    if len(ent) >= 2:
                        iid, qty = ent[0], ent[1]
                    else:
                        iid, qty = ent[0], 1
                else:
                    raise ValueError("each item must be a dict or tuple/list")
                to_process.append((iid, int(qty)))
        else:
            if item_id is None:
                raise ValueError("either items or item_id must be provided")
            to_process.append((item_id, int(quantity)))

        # validate quantities
        for _iid, _qty in to_process:
            if _qty <= 0:
                raise ValueError("quantities must be > 0")

        processed = []
        try:
            # Validate all menu items exist first
            for _iid, _qty in to_process:
                stmt_menu = select(Menu).where(Menu.item_id == _iid)
                res_menu = await session.exec(stmt_menu)
                menu_row = res_menu.one_or_none()
                if not menu_row:
                    raise ValueError(f"menu item {_iid} not found")

            # Process each cart entry: either increment existing or create new
            for _iid, _qty in to_process:
                stmt = select(CartItem).where(CartItem.username == username, CartItem.item_id == _iid)
                result = await session.exec(stmt)
                existing = result.one_or_none()

                if existing:
                    existing.quantity = existing.quantity + _qty
                    session.add(existing)
                    processed.append(existing)
                else:
                    new_cart = CartItem(username=username, item_id=_iid, quantity=_qty)
                    session.add(new_cart)
                    processed.append(new_cart)

            # commit once for the batch
            await session.commit()

            # refresh processed rows to pick up defaults
            for row in processed:
                await session.refresh(row)

        except Exception:
            await session.rollback()
            raise

        return processed

    async def update_cart(self, username: str, item_id: int, quantity: int, session: AsyncSession):
        """Update the quantity of a cart item. If quantity <= 0 the item is removed.

        Returns the updated CartItem or None if removed.
        """
        stmt = select(CartItem).where(CartItem.username == username, CartItem.item_id == item_id)
        result = await session.exec(stmt)
        existing = result.one_or_none()
        if not existing:
            raise ValueError("cart item not found")

        if quantity <= 0:
            # remove
            await session.delete(existing)
            await session.commit()
            return None
        else:
            existing.quantity = quantity
            session.add(existing)
            await session.commit()
            await session.refresh(existing)
            return existing
        
        
    async def delete_cart( self, username: str, session: AsyncSession):
        """Delete all cart items for a user."""
        stmt = select(CartItem).where(CartItem.username == username)
        result = await session.exec(stmt)
        cart_rows = result.all()
        for c in cart_rows:
            await session.delete(c)
        await session.commit()


    
    
    
    