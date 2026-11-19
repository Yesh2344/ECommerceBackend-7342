import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from . import models, schemas

logger = logging.getLogger(__name__)

class CartService:
    """Business logic for cart manipulation."""

    @staticmethod
    async def add_item(
        db: AsyncSession, payload: schemas.CartItemCreate
    ) -> models.CartItem:
        """Add a new item to the cart."""
        item = models.CartItem(**payload.dict())
        db.add(item)
        await db.commit()
        await db.refresh(item)
        logger.debug("Added cart item %s", item.id)
        return item

    @staticmethod
    async def list_items(db: AsyncSession) -> List[models.CartItem]:
        """Return all items currently in the cart."""
        result = await db.execute(select(models.CartItem).order_by(models.CartItem.added_at))
        items = result.scalars().all()
        logger.debug("Fetched %d cart items", len(items))
        return items

    @staticmethod
    async def remove_item(db: AsyncSession, item_id: int) -> None:
        """Delete a cart item by its primary key."""
        stmt = delete(models.CartItem).where(models.CartItem.id == item_id)
        result = await db.execute(stmt)
        if result.rowcount == 0:
            logger.warning("Attempted to delete non‑existent cart item %d", item_id)
            raise ValueError(f"Cart item {item_id} not found")
        await db.commit()
        logger.debug("Deleted cart item %d", item_id)