import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.order_schema import OrderCreate, OrderRead
from app.services.order_service import OrderService
from app.db import get_db

router = APIRouter()

@router.post("/orders/", response_model=OrderRead)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    service = OrderService(db)
    try:
        db_order = await service.create_order(order)
        logging.info(f"Order created via API: {db_order}")
        return db_order
    except Exception as e:
        logging.error(f"Error in create_order: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders/", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db)):
    service = OrderService(db)
    logging.info("Listing all orders")
    return service.list_orders()

@router.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    order = service.get_order_by_id(order_id)
    if not order:
        logging.warning(f"Order not found: {order_id}")
        raise HTTPException(status_code=404, detail="Order not found")
    logging.info(f"Fetched order: {order_id}")
    return order

@router.put("/orders/{order_id}", response_model=OrderRead)
async def update_order(order_id: int, order_update: OrderCreate, db: Session = Depends(get_db)):
    service = OrderService(db)
    try:
        order = await service.update_order(order_id, order_update)
        if not order:
            logging.warning(f"Order not found for update: {order_id}")
            raise HTTPException(status_code=404, detail="Order not found")
        logging.info(f"Order updated: {order_id}")
        return order
    except Exception as e:
        logging.error(f"Error updating order {order_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/orders/{order_id}")
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    result = await service.delete_order(order_id)
    if not result:
        logging.warning(f"Order not found for delete: {order_id}")
        raise HTTPException(status_code=404, detail="Order not found")
    logging.info(f"Order deleted: {order_id}")
    return {"detail": "Order deleted"}

@router.get("/orders/user/{user_id}", response_model=list[OrderRead])
def get_orders_by_user(user_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    try:
        return service.get_orders_by_user_id(user_id)
    except Exception as e:
        logging.error(f"Error fetching orders for user {user_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
