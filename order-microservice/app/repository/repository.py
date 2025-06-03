from sqlalchemy.orm import Session
from app.models.order import Order, OrderStatus
from app.schemas.order_schema import OrderCreate
import os
import asyncio
import logging

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, order_data: OrderCreate) -> Order:
        try:
            db_order = Order(
                product_id=order_data.product_id,
                quantity=order_data.quantity,
                status=OrderStatus.pending
            )
            self.db.add(db_order)
            self.db.commit()
            self.db.refresh(db_order)
            logging.info(f"OrderRepository: Created order {db_order.id}")
            return db_order
        except Exception as e:
            logging.error(f"OrderRepository: Error creating order: {e}")
            self.db.rollback()
            raise

    def list_orders(self):
        try:
            orders = self.db.query(Order).all()
            logging.info(f"OrderRepository: Listed {len(orders)} orders")
            return orders
        except Exception as e:
            logging.error(f"OrderRepository: Error listing orders: {e}")
            raise

    def get_order_by_id(self, order_id: int):
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                logging.warning(f"OrderRepository: Order not found {order_id}")
            else:
                logging.info(f"OrderRepository: Fetched order {order_id}")
            return order
        except Exception as e:
            logging.error(f"OrderRepository: Error fetching order {order_id}: {e}")
            raise

    def update_order(self, order_id: int, order_data: OrderCreate):
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                logging.warning(f"OrderRepository: Order not found for update {order_id}")
                return None
            order.product_id = order_data.product_id
            order.quantity = order_data.quantity
            self.db.commit()
            self.db.refresh(order)
            logging.info(f"OrderRepository: Updated order {order_id}")
            return order
        except Exception as e:
            logging.error(f"OrderRepository: Error updating order {order_id}: {e}")
            self.db.rollback()
            raise

    def delete_order(self, order_id: int):
        try:
            order = self.get_order_by_id(order_id)
            if not order:
                logging.warning(f"OrderRepository: Order not found for delete {order_id}")
                return False
            self.db.delete(order)
            self.db.commit()
            logging.info(f"OrderRepository: Deleted order {order_id}")
            return True
        except Exception as e:
            logging.error(f"OrderRepository: Error deleting order {order_id}: {e}")
            self.db.rollback()
            raise
