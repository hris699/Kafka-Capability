from pydantic import BaseModel
from enum import Enum

class OrderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

class OrderCreate(BaseModel):
    product_id: str
    quantity: int
    user_id: int

class OrderRead(BaseModel):
    id: int
    product_id: str
    quantity: int
    status: OrderStatus
    user_id: int

    class Config:
        from_attributes = True
