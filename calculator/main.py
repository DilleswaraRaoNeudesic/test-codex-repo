from fastapi import FastAPI, HTTPException
from .models import OperationRequest, OperationResponse


app = FastAPI(title="Calculator API")


@app.post("/add", response_model=OperationResponse)
def add(payload: OperationRequest) -> OperationResponse:
    return OperationResponse(result=payload.a + payload.b)


@app.post("/subtract", response_model=OperationResponse)
def subtract(payload: OperationRequest) -> OperationResponse:
    return OperationResponse(result=payload.a - payload.b)


@app.post("/multiply", response_model=OperationResponse)
def multiply(payload: OperationRequest) -> OperationResponse:
    return OperationResponse(result=payload.a * payload.b)


@app.post("/divide", response_model=OperationResponse)
def divide(payload: OperationRequest) -> OperationResponse:
    if payload.b == 0:
        raise HTTPException(status_code=400, detail="Division by zero is not allowed")
    return OperationResponse(result=payload.a / payload.b)

