from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class OrderStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(100), index=True)  
    quantity = Column(Integer)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
