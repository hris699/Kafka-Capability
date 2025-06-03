from sqlalchemy.orm import Session
from app.repository.repository import OrderRepository
import httpx
from app.schemas.order_schema import OrderCreate
from app.models.order import Order
import os
import logging

class InventoryService:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def check_stock(self, product_id: str, quantity: int) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/inventory/{product_id}")
                if response.status_code == 200:
                    data = response.json()
                    logging.info(f"Checked stock for {product_id}: {data.get('quantity', 0)} available")
                    return data.get("quantity", 0) >= quantity
                logging.warning(f"Failed to check stock for {product_id}: {response.text}")
                return False
            except Exception as e:
                logging.error(f"Error checking stock for {product_id}: {e}")
                return False

    async def reduce_stock(self, product_id: str, quantity: int) -> None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/inventory/reduce",
                    json={"product_id": product_id, "quantity": quantity}
                )
                if response.status_code != 200:
                    logging.error(f"Failed to update inventory for {product_id}: {response.text}")
                    raise Exception("Failed to update inventory")
                logging.info(f"Reduced stock for {product_id} by {quantity}")
            except Exception as e:
                logging.error(f"Error reducing stock for {product_id}: {e}")
                raise

    async def increase_stock(self, product_id: str, quantity: int) -> None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/inventory/increase",
                    json={"product_id": product_id, "quantity": quantity}
                )
                if response.status_code != 200:
                    logging.error(f"Failed to increase inventory for {product_id}: {response.text}")
                    raise Exception("Failed to increase inventory")
                logging.info(f"Increased stock for {product_id} by {quantity}")
            except Exception as e:
                logging.error(f"Error increasing stock for {product_id}: {e}")
                raise

class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OrderRepository(db)
        self.inventory_service = InventoryService(base_url=os.getenv("INVENTORY_BASE_URL", "http://localhost:8001"))

    async def create_order(self, order_data: OrderCreate) -> Order:
        logging.info(f"create_order called with: {order_data}")
        try:
            if not await self.inventory_service.check_stock(order_data.product_id, order_data.quantity):
                logging.warning("Insufficient inventory for product %s", order_data.product_id)
                raise Exception("Insufficient inventory")
            await self.inventory_service.reduce_stock(order_data.product_id, order_data.quantity)
            new_order = self.repo.create_order(order_data)
            logging.info(f"Order created: {new_order}")
            return new_order
        except Exception as e:
            logging.error(f"Error in OrderService.create_order: {e}")
            raise

    def list_orders(self):
        try:
            orders = self.repo.list_orders()
            logging.info(f"Listed {len(orders)} orders")
            return orders
        except Exception as e:
            logging.error(f"Error in OrderService.list_orders: {e}")
            raise

    def get_order_by_id(self, order_id: int):
        try:
            order = self.repo.get_order_by_id(order_id)
            if not order:
                logging.warning(f"Order not found: {order_id}")
            else:
                logging.info(f"Fetched order: {order_id}")
            return order
        except Exception as e:
            logging.error(f"Error in OrderService.get_order_by_id: {e}")
            raise

    async def update_order(self, order_id: int, order_data: OrderCreate):
        try:
            order = self.repo.get_order_by_id(order_id)
            if not order:
                logging.warning(f"Order not found for update: {order_id}")
                return None
            if order.product_id != order_data.product_id or order.quantity != order_data.quantity:
                if order.product_id != order_data.product_id:
                    await self.inventory_service.increase_stock(order.product_id, order.quantity)
                    if not await self.inventory_service.check_stock(order_data.product_id, order_data.quantity):
                        logging.warning("Insufficient inventory for new product %s", order_data.product_id)
                        raise Exception("Insufficient inventory for new product")
                    await self.inventory_service.reduce_stock(order_data.product_id, order_data.quantity)
                else:
                    diff = order_data.quantity - order.quantity
                    if diff > 0:
                        if not await self.inventory_service.check_stock(order.product_id, diff):
                            logging.warning("Insufficient inventory for update on product %s", order.product_id)
                            raise Exception("Insufficient inventory for update")
                        await self.inventory_service.reduce_stock(order.product_id, diff)
                    elif diff < 0:
                        await self.inventory_service.increase_stock(order.product_id, -diff)
            updated_order = self.repo.update_order(order_id, order_data)
            logging.info(f"Order updated: {order_id}")
            return updated_order
        except Exception as e:
            logging.error(f"Error in OrderService.update_order: {e}")
            raise

    async def delete_order(self, order_id: int):
        try:
            order = self.repo.get_order_by_id(order_id)
            if not order:
                logging.warning(f"Order not found for delete: {order_id}")
                return False
            await self.inventory_service.increase_stock(order.product_id, order.quantity)
            result = self.repo.delete_order(order_id)
            logging.info(f"Order deleted: {order_id}")
            return result
        except Exception as e:
            logging.error(f"Error in OrderService.delete_order: {e}")
            raise
