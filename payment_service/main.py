import os
import aiosqlite
from fastapi import FastAPI, HTTPException
from models.schemas import PaymentChargeRequest, PaymentRefundRequest, PaymentResult


DB_PATH = os.getenv("PAYMENT_DB", os.path.join(os.path.dirname(__file__), "payment.sqlite3"))

app = FastAPI(title="Payment Service")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                amount REAL NOT NULL,
                success INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.post("/payments/charge", response_model=PaymentResult)
async def charge(req: PaymentChargeRequest):
    # Simulate payment logic: fail if amount <= 0 or customer flagged (e.g., id starting with "X")
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    success = not req.customer_id.upper().startswith("X")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN")
        try:
            cursor = await db.execute(
                "INSERT INTO payments (order_id, amount, success) VALUES (?, ?, ?)",
                (req.order_id, req.amount, 1 if success else 0),
            )
            await db.commit()
            transaction_id = cursor.lastrowid
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Charge failed")

    if not success:
        return PaymentResult(success=False, transaction_id=transaction_id, error="Payment declined")
    return PaymentResult(success=True, transaction_id=transaction_id)


@app.post("/payments/refund", response_model=PaymentResult)
async def refund(req: PaymentRefundRequest):
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN")
        try:
            cursor = await db.execute(
                "INSERT INTO payments (order_id, amount, success) VALUES (?, ?, ?)",
                (req.order_id, -abs(req.amount), 1),
            )
            await db.commit()
            transaction_id = cursor.lastrowid
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Refund failed")
    return PaymentResult(success=True, transaction_id=transaction_id)

