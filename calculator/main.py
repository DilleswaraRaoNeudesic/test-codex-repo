from fastapi import FastAPI, HTTPException
from calculator.models import OperationRequest, OperationResponse


app = FastAPI(title="Calculator API")


@app.post("/add", response_model=OperationResponse)
def add(req: OperationRequest) -> OperationResponse:
    return OperationResponse(result=req.a + req.b)


@app.post("/subtract", response_model=OperationResponse)
def subtract(req: OperationRequest) -> OperationResponse:
    return OperationResponse(result=req.a - req.b)


@app.post("/multiply", response_model=OperationResponse)
def multiply(req: OperationRequest) -> OperationResponse:
    return OperationResponse(result=req.a * req.b)


@app.post("/divide", response_model=OperationResponse)
def divide(req: OperationRequest) -> OperationResponse:
    if req.b == 0:
        raise HTTPException(status_code=400, detail="Division by zero")
    return OperationResponse(result=req.a / req.b)

