from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base

class CartItem(Base):
    """Persisted cart item."""
    __tablename__ = "cart_items"

    id: int = Column(Integer, primary_key=True, index=True)
    product_id: str = Column(String, nullable=False)
    name: str = Column(String, nullable=False)
    price: float = Column(Float, nullable=False)
    quantity: int = Column(Integer, nullable=False, default=1)
    added_at: datetime = Column(DateTime, default=datetime.utcnow)

    # In a real system we would link to a User table:
    # user_id = Column(Integer, ForeignKey("users.id"))
    # user = relationship("User", back_populates="cart_items")