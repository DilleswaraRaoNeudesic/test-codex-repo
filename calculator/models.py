from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class Operands(BaseModel):
    a: float
    b: float


class SingleOperand(BaseModel):
    a: float


class Result(BaseModel):
    result: float


class HistoryItem(BaseModel):
    operation: str
    a: Optional[float] = None
    b: Optional[float] = None
    result: float
