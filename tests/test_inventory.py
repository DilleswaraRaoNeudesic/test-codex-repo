import pytest
import asyncio
from httpx import AsyncClient
from inventory_service.main import app, DB_PATH, init_db
from models.schemas import InventoryItem
import aiosqlite


@pytest.mark.asyncio
async def test_inventory_reserve_and_release():
    await init_db()
    # Seed stock
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM inventory")
        await db.execute("INSERT INTO inventory (sku, quantity) VALUES (?, ?)", ("ABC", 10))
        await db.commit()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(
            "/inventory/reserve",
            json={"items": [{"sku": "ABC", "quantity": 5}]},
        )
        assert resp.status_code == 200
        resp = await ac.post(
            "/inventory/release",
            json={"items": [{"sku": "ABC", "quantity": 5}]},
        )
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_inventory_reserve_insufficient():
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM inventory")
        await db.execute("INSERT INTO inventory (sku, quantity) VALUES (?, ?)", ("ABC", 2))
        await db.commit()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(
            "/inventory/reserve",
            json={"items": [{"sku": "ABC", "quantity": 5}]},
        )
        assert resp.status_code == 400

