import os
from typing import List

import aiosqlite
import httpx
from fastapi import FastAPI, HTTPException

from models.schemas import (
    OrderCreateRequest,
    OrderResponse,
    InventoryItem,
    InventoryReserveRequest,
    InventoryReleaseRequest,
    PaymentChargeRequest,
)


# Keep exported names for tests, but do not rely on them internally
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://localhost:8001")
PAYMENT_URL = os.getenv("PAYMENT_URL", "http://localhost:8002")
DB_PATH = os.getenv("ORDER_DB", os.path.join(os.path.dirname(__file__), "orders.sqlite3"))

app = FastAPI(title="Order Service")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                status TEXT NOT NULL,
                total_amount REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                sku TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL
            )
            """
        )
        await db.commit()


@app.on_event("startup")
async def on_startup():
    await init_db()


def _get_client_for_url(base_url: str) -> httpx.AsyncClient:
    # In test mode, route to local ASGI apps without network
    if base_url.startswith("http://test_inv"):
        from inventory_service.main import app as inv_app
        return httpx.AsyncClient(transport=httpx.ASGITransport(app=inv_app), base_url="http://test_inv")
    if base_url.startswith("http://test_pay"):
        from payment_service.main import app as pay_app
        return httpx.AsyncClient(transport=httpx.ASGITransport(app=pay_app), base_url="http://test_pay")
    return httpx.AsyncClient(timeout=5.0)

@app.post("/orders", response_model=OrderResponse)
async def create_order(req: OrderCreateRequest):
    inventory_url = os.getenv("INVENTORY_URL", "http://localhost:8001")
    payment_url = os.getenv("PAYMENT_URL", "http://localhost:8002")
    # Ensure DB schema exists when running under test clients
    await init_db()
    # Reserve inventory first
    reserve_payload = InventoryReserveRequest(
        items=[InventoryItem(sku=i.sku, quantity=i.quantity) for i in req.items]
    )
    async with _get_client_for_url(inventory_url) as client:
        try:
            inv_resp = await client.post(f"{inventory_url}/inventory/reserve", json=reserve_payload.model_dump())
            inv_resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Inventory reservation failed")
        except Exception:
            raise HTTPException(status_code=503, detail="Inventory service unavailable")

    # Charge payment
    amount = req.total_amount
    async with _get_client_for_url(payment_url) as client:
        try:
            pay_resp = await client.post(
                f"{payment_url}/payments/charge",
                json=PaymentChargeRequest(order_id=None, customer_id=req.customer_id, amount=amount).model_dump(),
            )
            pay_resp.raise_for_status()
            pay_data = pay_resp.json()
            if not pay_data.get("success"):
                # Release inventory on payment failure
                async with _get_client_for_url(inventory_url) as inv_client:
                    await inv_client.post(
                        f"{inventory_url}/inventory/release",
                        json=InventoryReleaseRequest(
                            items=[InventoryItem(sku=i.sku, quantity=i.quantity) for i in req.items]
                        ).model_dump(),
                    )
                raise HTTPException(status_code=402, detail="Payment declined")
        except httpx.HTTPStatusError as e:
            # release inventory
            async with _get_client_for_url(inventory_url) as inv_client:
                await inv_client.post(
                    f"{inventory_url}/inventory/release",
                    json=InventoryReleaseRequest(
                        items=[InventoryItem(sku=i.sku, quantity=i.quantity) for i in req.items]
                    ).model_dump(),
                )
            raise HTTPException(status_code=e.response.status_code, detail="Payment failed")
        except HTTPException:
            # propagate intentional HTTP exceptions like 402 decline
            raise
        except Exception:
            async with _get_client_for_url(inventory_url) as inv_client:
                await inv_client.post(
                    f"{inventory_url}/inventory/release",
                    json=InventoryReleaseRequest(
                        items=[InventoryItem(sku=i.sku, quantity=i.quantity) for i in req.items]
                    ).model_dump(),
                )
            raise HTTPException(status_code=503, detail="Payment service unavailable")

    # Persist order
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN")
        try:
            cursor = await db.execute(
                "INSERT INTO orders (customer_id, status, total_amount) VALUES (?, ?, ?)",
                (req.customer_id, "created", amount),
            )
            order_id = cursor.lastrowid
            for item in req.items:
                await db.execute(
                    "INSERT INTO order_items (order_id, sku, quantity, price) VALUES (?, ?, ?, ?)",
                    (order_id, item.sku, item.quantity, item.price),
                )
            await db.commit()
        except Exception:
            await db.rollback()
            # compensate: refund payment? For simplicity, leave as-is; inventory already reserved then released only on payment failure.
            raise HTTPException(status_code=500, detail="Order persistence failed")

    return OrderResponse(order_id=order_id, status="created")


@app.get("/orders")
async def list_orders():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id, customer_id, status, total_amount FROM orders ORDER BY id DESC")
        rows = await cursor.fetchall()
    return {
        "orders": [
            {"id": r[0], "customer_id": r[1], "status": r[2], "total_amount": r[3]} for r in rows
        ]
    }
