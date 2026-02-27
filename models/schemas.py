from typing import List, Optional
from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    sku: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    price: float = Field(..., ge=0.0)


class OrderCreateRequest(BaseModel):
    customer_id: str
    items: List[OrderItem]

    @property
    def total_amount(self) -> float:
        return sum(i.quantity * i.price for i in self.items)


class OrderResponse(BaseModel):
    order_id: int
    status: str


class InventoryItem(BaseModel):
    sku: str
    quantity: int


class InventoryReserveRequest(BaseModel):
    items: List[InventoryItem]


class InventoryReleaseRequest(BaseModel):
    items: List[InventoryItem]


class PaymentChargeRequest(BaseModel):
    order_id: Optional[int] = None
    customer_id: str
    amount: float


class PaymentRefundRequest(BaseModel):
    order_id: int
    amount: float


class PaymentResult(BaseModel):
    success: bool
    transaction_id: Optional[int] = None
    error: Optional[str] = None

