import pytest
import httpx
from httpx import AsyncClient
from order_service.main import app, init_db, INVENTORY_URL, PAYMENT_URL
from inventory_service.main import app as inv_app, init_db as inv_init_db, DB_PATH as INV_DB
from payment_service.main import app as pay_app, init_db as pay_init_db
import aiosqlite


@pytest.mark.asyncio
async def test_order_happy_path(monkeypatch):
    await inv_init_db()
    async with aiosqlite.connect(INV_DB) as db:
        await db.execute("DELETE FROM inventory")
        await db.execute("INSERT INTO inventory (sku, quantity) VALUES (?, ?)", ("ABC", 10))
        await db.commit()

    # Patch URLs to point to in-app clients
    monkeypatch.setenv("INVENTORY_URL", "http://test_inv")
    monkeypatch.setenv("PAYMENT_URL", "http://test_pay")

    async with AsyncClient(app=inv_app, base_url="http://test_inv") as inv_client:
        async with AsyncClient(app=pay_app, base_url="http://test_pay") as pay_client:
            async with AsyncClient(app=app, base_url="http://test") as ac:
                # Monkeypatch httpx.AsyncClient to route to our test clients based on base_url
                class _RouterClient(AsyncClient):
                    async def post(self, url, *args, **kwargs):
                        if url.startswith("http://test_inv"):
                            return await inv_client.post(url.replace("http://test_inv", ""), *args, **kwargs)
                        if url.startswith("http://test_pay"):
                            return await pay_client.post(url.replace("http://test_pay", ""), *args, **kwargs)
                        return await super().post(url, *args, **kwargs)

                monkeypatch.setattr(httpx, "AsyncClient", _RouterClient)

                resp = await ac.post(
                    "/orders",
                    json={
                        "customer_id": "CUST1",
                        "items": [{"sku": "ABC", "quantity": 2, "price": 10.0}],
                    },
                )
                assert resp.status_code == 200
                data = resp.json()
                assert data["status"] == "created"


@pytest.mark.asyncio
async def test_order_inventory_failure(monkeypatch):
    await inv_init_db()
    async with aiosqlite.connect(INV_DB) as db:
        await db.execute("DELETE FROM inventory")
        await db.execute("INSERT INTO inventory (sku, quantity) VALUES (?, ?)", ("ABC", 1))
        await db.commit()

    monkeypatch.setenv("INVENTORY_URL", "http://test_inv")
    monkeypatch.setenv("PAYMENT_URL", "http://test_pay")

    async with AsyncClient(app=inv_app, base_url="http://test_inv") as inv_client:
        async with AsyncClient(app=pay_app, base_url="http://test_pay") as pay_client:
            async with AsyncClient(app=app, base_url="http://test") as ac:
                class _RouterClient(AsyncClient):
                    async def post(self, url, *args, **kwargs):
                        if url.startswith("http://test_inv"):
                            return await inv_client.post(url.replace("http://test_inv", ""), *args, **kwargs)
                        if url.startswith("http://test_pay"):
                            return await pay_client.post(url.replace("http://test_pay", ""), *args, **kwargs)
                        return await super().post(url, *args, **kwargs)

                monkeypatch.setattr(httpx, "AsyncClient", _RouterClient)

                resp = await ac.post(
                    "/orders",
                    json={
                        "customer_id": "CUST1",
                        "items": [{"sku": "ABC", "quantity": 5, "price": 10.0}],
                    },
                )
                assert resp.status_code == 400


@pytest.mark.asyncio
async def test_order_payment_failure(monkeypatch):
    await inv_init_db()
    async with aiosqlite.connect(INV_DB) as db:
        await db.execute("DELETE FROM inventory")
        await db.execute("INSERT INTO inventory (sku, quantity) VALUES (?, ?)", ("ABC", 10))
        await db.commit()

    monkeypatch.setenv("INVENTORY_URL", "http://test_inv")
    monkeypatch.setenv("PAYMENT_URL", "http://test_pay")

    async with AsyncClient(app=inv_app, base_url="http://test_inv") as inv_client:
        async with AsyncClient(app=pay_app, base_url="http://test_pay") as pay_client:
            async with AsyncClient(app=app, base_url="http://test") as ac:
                class _RouterClient(AsyncClient):
                    async def post(self, url, *args, **kwargs):
                        if url.startswith("http://test_inv"):
                            return await inv_client.post(url.replace("http://test_inv", ""), *args, **kwargs)
                        if url.startswith("http://test_pay"):
                            return await pay_client.post(url.replace("http://test_pay", ""), *args, **kwargs)
                        return await super().post(url, *args, **kwargs)

                monkeypatch.setattr(httpx, "AsyncClient", _RouterClient)

                resp = await ac.post(
                    "/orders",
                    json={
                        "customer_id": "XBAD",  # triggers payment decline
                        "items": [{"sku": "ABC", "quantity": 2, "price": 10.0}],
                    },
                )
                assert resp.status_code == 402
