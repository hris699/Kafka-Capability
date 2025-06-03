from sqlalchemy.orm import Session
from app.models.order import Order, OrderStatus
from app.schemas.order_schema import OrderCreate
import os
import asyncio

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, order_data: OrderCreate) -> Order:
        db_order = Order(
            product_id=order_data.product_id,
            quantity=order_data.quantity,
            status=OrderStatus.pending
        )
        self.db.add(db_order)
        self.db.commit()
        self.db.refresh(db_order)
        return db_order

    def list_orders(self):
        return self.db.query(Order).all()

    def get_order_by_id(self, order_id: int):
        return self.db.query(Order).filter(Order.id == order_id).first()

    def update_order(self, order_id: int, order_data: OrderCreate):
        order = self.get_order_by_id(order_id)
        if not order:
            return None
        order.product_id = order_data.product_id
        order.quantity = order_data.quantity
        self.db.commit()
        self.db.refresh(order)
        return order

    def delete_order(self, order_id: int):
        order = self.get_order_by_id(order_id)
        if not order:
            return False
        self.db.delete(order)
        self.db.commit()
        return True
