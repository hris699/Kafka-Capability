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
        return db_order
    except Exception as e:
        print("Error in create_order:", e)  # Add this line
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders/", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db)):
    service = OrderService(db)
    return service.list_orders()

@router.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    order = service.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/orders/{order_id}", response_model=OrderRead)
async def update_order(order_id: int, order_update: OrderCreate, db: Session = Depends(get_db)):
    service = OrderService(db)
    try:
        order = await service.update_order(order_id, order_update)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/orders/{order_id}")
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    service = OrderService(db)
    result = await service.delete_order(order_id)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"detail": "Order deleted"}
