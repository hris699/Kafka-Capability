from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentResponse
import logging
from sqlalchemy.exc import SQLAlchemyError
import bcrypt

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/payments/", response_model=PaymentResponse)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating new payment for order ID #{payment.order_id}")
    
    # Check if a successful payment already exists for this order
    existing_payment = db.query(Payment).filter(
        Payment.order_id == payment.order_id,
        Payment.status == PaymentStatus.SUCCESSFUL
    ).first()
    
    if existing_payment:
        logger.warning(f"Payment already exists for order ID #{payment.order_id}")
        raise HTTPException(
            status_code=400,
            detail=f"Payment for order ID #{payment.order_id} has already been processed successfully"
        )

    try:
        hashed_cvv = bcrypt.hashpw(payment.cvv.encode('utf-8'), bcrypt.gensalt())
        
        db_payment = Payment(
            order_id=payment.order_id,
            amount=payment.amount,
            card_number=payment.card_number,
            card_holder_name=payment.card_holder_name,
            expiry_date=payment.expiry_date,
            hashed_cvv=hashed_cvv.decode('utf-8'),  # Store the hashed CVV
            status=PaymentStatus.SUCCESSFUL  
        )
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        logger.info(f"Successfully created payment with ID {db_payment.id}")
        return db_payment
    except SQLAlchemyError as e:
        logger.error(f"Database error creating payment: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create payment due to database error")
    except Exception as e:
        logger.error(f"Unexpected error creating payment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating payment")

@router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching payment with ID {payment_id}")
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if payment is None:
            logger.warning(f"Payment not found with ID {payment_id}")
            raise HTTPException(status_code=404, detail="Payment not found")
        logger.info(f"Successfully fetched payment with ID {payment_id}")
        return payment
    except SQLAlchemyError as e:
        logger.error(f"Error fetching payment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch payment")
    except Exception as e:
        logger.error(f"Unexpected error fetching payment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payments/order/{order_id}", response_model=List[PaymentResponse])
def get_payments_by_order(order_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching payments for order {order_id}")
    try:
        payments = db.query(Payment).filter(Payment.order_id == order_id).all()
        logger.info(f"Successfully fetched {len(payments)} payments for order {order_id}")
        return payments
    except SQLAlchemyError as e:
        logger.error(f"Error fetching payments for order {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch payments")
    except Exception as e:
        logger.error(f"Unexpected error fetching payments: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 