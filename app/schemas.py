from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

class CartItemCreate(BaseModel):
    """Payload for adding an item to the cart."""
    product_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    quantity: int = Field(1, gt=0)

class CartItemResponse(BaseModel):
    """Read‑only representation of a cart item."""
    id: int
    product_id: str
    name: str
    price: float
    quantity: int
    added_at: datetime

    class Config:
        orm_mode = True

class CheckoutRequest(BaseModel):
    """Payload for payment checkout."""
    cart_item_ids: List[int] = Field(..., min_items=1)

class CheckoutResponse(BaseModel):
    """Result of a mock payment."""
    success: bool
    payment_intent_id: str
    amount_charged: float
    currency: str = "usd"