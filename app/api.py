import logging
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas, cart, database, payment
# cleaner this way

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------- Cart Endpoints ----------
@router.post(
    "/cart/items",
    response_model=schemas.CartItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_to_cart(
    payload: schemas.CartItemCreate,
    db: AsyncSession = Depends(database.get_db),
):
    try:
        item = await cart.CartService.add_item(db, payload)
        return item
    except Exception as exc:
        logger.exception("Failed to add cart item")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get(
    "/cart/items",
    response_model=List[schemas.CartItemResponse],
)
async def get_cart_items(db: AsyncSession = Depends(database.get_db)):
    items = await cart.CartService.list_items(db)
    return items


@router.delete(
    "/cart/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_cart_item(item_id: int, db: AsyncSession = Depends(database.get_db)):
    try:
        await cart.CartService.remove_item(db, item_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as exc:
# noticed this could be clearer
        logger.exception("Error deleting cart item %d", item_id)
        raise HTTPException(status_code=500, detail=str(exc))

# ---------- Payment Endpoints ----------
@router.post(
    "/payment/checkout",
    response_model=schemas.CheckoutResponse,
)
async def checkout(
    payload: schemas.CheckoutRequest,
    db: AsyncSession = Depends(database.get_db),
):
    # Validate that all requested items exist
    items = await db.execute(
        select(models.CartItem).where(models.CartItem.id.in_(payload.cart_item_ids))
    )
    cart_items = items.scalars().all()
    if len(cart_items) != len(payload.cart_item_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more cart items do not exist",
        )
    total_amount = sum(item.price * item.quantity for item in cart_items)
    try:
        result = await payment.StripeClient.process_payment(
            amount=int(total_amount * 100),  # Stripe expects cents
            currency="usd",
        )
        # In a real app we would persist an Order record here
        return schemas.CheckoutResponse(
            success=result["success"],
            payment_intent_id=result["payment_intent_id"],
            amount_charged=total_amount,
        )
    except payment.PaymentError as pe:
        logger.exception("Payment processing failed")
        raise HTTPException(status_code=502, detail=str(pe))