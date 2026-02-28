from pydantic import BaseModel


class OperationRequest(BaseModel):
    a: float
    b: float


class OperationResponse(BaseModel):
    result: float

