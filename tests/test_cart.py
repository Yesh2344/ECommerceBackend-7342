import asyncio

import pytest
from httpx import AsyncClient

from app.main import app
from app.database import drop_db, init_db, get_db
from app import models

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def reset_db():
    """Reset the database before each test."""
    await drop_db()
    await init_db()
    yield
    await drop_db()

@pytest.mark.asyncio
async def test_cart_flow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Add an item
        payload = {
            "product_id": "sku_123",
            "name": "Test Product",
            "price": 19.99,
            "quantity": 2,
        }
        resp = await client.post("/cart/items", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        item_id = data["id"]
        assert data["name"] == payload["name"]
        assert data["quantity"] == payload["quantity"]

        # List items
        resp = await client.get("/cart/items")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert items[0]["id"] == item_id

        # Checkout (mock payment)
        checkout_payload = {"cart_item_ids": [item_id]}
        resp = await client.post("/payment/checkout", json=checkout_payload)
        assert resp.status_code == 200
        checkout_data = resp.json()
        assert checkout_data["success"] is True
        assert checkout_data["amount_charged"] == pytest.approx(39.98, rel=1e-3)

        # Delete item
        resp = await client.delete(f"/cart/items/{item_id}")
        assert resp.status_code == 204

        # Ensure cart is empty
        resp = await client.get("/cart/items")
        assert resp.status_code == 200
        assert resp.json() == []