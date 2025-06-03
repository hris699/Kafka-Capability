from sqlalchemy.orm import Session
from app.repository.repository import OrderRepository
import httpx
from app.schemas.order_schema import OrderCreate
from app.models.order import Order
import os

class InventoryService:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def check_stock(self, product_id: str, quantity: int) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/inventory/{product_id}")
            if response.status_code == 200:
                data = response.json()
                return data.get("quantity", 0) >= quantity
            return False

    async def reduce_stock(self, product_id: str, quantity: int) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/inventory/reduce",
                json={"product_id": product_id, "quantity": quantity}
            )
            if response.status_code != 200:
                raise Exception("Failed to update inventory")

    async def increase_stock(self, product_id: str, quantity: int) -> None:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/inventory/increase",
                json={"product_id": product_id, "quantity": quantity}
            )
            if response.status_code != 200:
                raise Exception("Failed to increase inventory")

class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = OrderRepository(db)
        self.inventory_service = InventoryService(base_url=os.getenv("INVENTORY_BASE_URL", "http://localhost:8001"))

    async def create_order(self, order_data: OrderCreate) -> Order:
        if not await self.inventory_service.check_stock(order_data.product_id, order_data.quantity):
            raise Exception("Insufficient inventory")
        await self.inventory_service.reduce_stock(order_data.product_id, order_data.quantity)
        return self.repo.create_order(order_data)

    def list_orders(self):
        return self.repo.list_orders()

    def get_order_by_id(self, order_id: int):
        return self.repo.get_order_by_id(order_id)

    async def update_order(self, order_id: int, order_data: OrderCreate):
        order = self.repo.get_order_by_id(order_id)
        if not order:
            return None
        if order.product_id != order_data.product_id or order.quantity != order_data.quantity:
            if order.product_id != order_data.product_id:
                await self.inventory_service.increase_stock(order.product_id, order.quantity)
                if not await self.inventory_service.check_stock(order_data.product_id, order_data.quantity):
                    raise Exception("Insufficient inventory for new product")
                await self.inventory_service.reduce_stock(order_data.product_id, order_data.quantity)
            else:
                diff = order_data.quantity - order.quantity
                if diff > 0:
                    if not await self.inventory_service.check_stock(order.product_id, diff):
                        raise Exception("Insufficient inventory for update")
                    await self.inventory_service.reduce_stock(order.product_id, diff)
                elif diff < 0:
                    await self.inventory_service.increase_stock(order.product_id, -diff)
        return self.repo.update_order(order_id, order_data)

    async def delete_order(self, order_id: int):
        order = self.repo.get_order_by_id(order_id)
        if not order:
            return False
        await self.inventory_service.increase_stock(order.product_id, order.quantity)
        return self.repo.delete_order(order_id)
