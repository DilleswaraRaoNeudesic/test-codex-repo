import pytest
from httpx import AsyncClient
from payment_service.main import app, init_db


@pytest.mark.asyncio
async def test_payment_charge_success():
    await init_db()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(
            "/payments/charge",
            json={"order_id": 1, "customer_id": "CUST1", "amount": 100.0},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_payment_charge_declined():
    await init_db()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(
            "/payments/charge",
            json={"order_id": 1, "customer_id": "XBAD", "amount": 100.0},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is False

