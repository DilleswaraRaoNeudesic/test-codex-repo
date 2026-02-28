from collections import deque
from fastapi import FastAPI, HTTPException
from calculator.models import Operands, SingleOperand, Result, HistoryItem


app = FastAPI(title="Calculator API")
history: deque[HistoryItem] = deque(maxlen=10)


def record(item: HistoryItem) -> None:
    history.appendleft(item)


@app.post("/add", response_model=Result)
def add(body: Operands) -> Result:
    res = body.a + body.b
    record(HistoryItem(operation="add", a=body.a, b=body.b, result=res))
    return Result(result=res)


@app.post("/subtract", response_model=Result)
def subtract(body: Operands) -> Result:
    res = body.a - body.b
    record(HistoryItem(operation="subtract", a=body.a, b=body.b, result=res))
    return Result(result=res)


@app.post("/multiply", response_model=Result)
def multiply(body: Operands) -> Result:
    res = body.a * body.b
    record(HistoryItem(operation="multiply", a=body.a, b=body.b, result=res))
    return Result(result=res)


@app.post("/divide", response_model=Result)
def divide(body: Operands) -> Result:
    if body.b == 0:
        raise HTTPException(status_code=400, detail="Division by zero")
    res = body.a / body.b
    record(HistoryItem(operation="divide", a=body.a, b=body.b, result=res))
    return Result(result=res)


@app.post("/power", response_model=Result)
def power(body: Operands) -> Result:
    res = body.a ** body.b
    record(HistoryItem(operation="power", a=body.a, b=body.b, result=res))
    return Result(result=res)


@app.post("/sqrt", response_model=Result)
def sqrt(body: SingleOperand) -> Result:
    if body.a < 0:
        raise HTTPException(status_code=400, detail="Square root of negative number")
    # Use exponent for sqrt to avoid extra imports
    res = body.a ** 0.5
    record(HistoryItem(operation="sqrt", a=body.a, result=res))
    return Result(result=res)


@app.get("/history")
def get_history() -> list[HistoryItem]:
    return list(history)

