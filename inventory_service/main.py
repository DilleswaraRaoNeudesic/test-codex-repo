import asyncio
import os
from typing import List

import aiosqlite
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from models.schemas import (
    InventoryItem,
    InventoryReserveRequest,
    InventoryReleaseRequest,
)


DB_PATH = os.getenv("INVENTORY_DB", os.path.join(os.path.dirname(__file__), "inventory.sqlite3"))

app = FastAPI(title="Inventory Service")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                sku TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL
            )
            """
        )
        await db.commit()


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.post("/inventory/set_stock")
async def set_stock(items: List[InventoryItem]):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN")
        try:
            for item in items:
                await db.execute(
                    "INSERT INTO inventory (sku, quantity) VALUES (?, ?) ON CONFLICT(sku) DO UPDATE SET quantity=excluded.quantity",
                    (item.sku, item.quantity),
                )
            await db.commit()
        except Exception:
            await db.rollback()
            raise
    return {"updated": len(items)}


@app.get("/inventory/levels")
async def get_levels():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT sku, quantity FROM inventory")
        rows = await cursor.fetchall()
    return {"items": [{"sku": r[0], "quantity": r[1]} for r in rows]}


@app.post("/inventory/reserve")
async def reserve(req: InventoryReserveRequest):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN")
        try:
            # Check availability
            for item in req.items:
                cursor = await db.execute("SELECT quantity FROM inventory WHERE sku=?", (item.sku,))
                row = await cursor.fetchone()
                available = row[0] if row else 0
                if available < item.quantity:
                    await db.rollback()
                    raise HTTPException(status_code=400, detail=f"Insufficient stock for {item.sku}")
            # Decrement quantities
            for item in req.items:
                await db.execute(
                    "UPDATE inventory SET quantity = quantity - ? WHERE sku=?",
                    (item.quantity, item.sku),
                )
            await db.commit()
        except HTTPException:
            raise
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Reservation failed")
    return {"reserved": True}


@app.post("/inventory/release")
async def release(req: InventoryReleaseRequest):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN")
        try:
            for item in req.items:
                await db.execute(
                    "UPDATE inventory SET quantity = quantity + ? WHERE sku=?",
                    (item.quantity, item.sku),
                )
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Release failed")
    return {"released": True}

