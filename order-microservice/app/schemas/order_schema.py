from pydantic import BaseModel
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

class OrderCreate(BaseModel):
    product_id: str
    quantity: int

class OrderRead(BaseModel):
    id: int
    product_id: str
    quantity: int
    status: OrderStatus

    class Config:
        from_attributes = True
