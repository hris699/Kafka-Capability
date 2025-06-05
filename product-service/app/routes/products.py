from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import requests
import logging
from pydantic import BaseModel
from app.db.database import get_db
from app.models.product import Product, Category
from app.schemas.product import Product as ProductSchema, ProductCreate, ProductUpdate
from app.core.auth import verify_admin, verify_token

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

class PaginatedProductsResponse(BaseModel):
    products: List[ProductSchema]
    total: int
    page: int
    totalPages: int

@router.get("", response_model=PaginatedProductsResponse)  # Empty string for root path
@router.get("/", response_model=PaginatedProductsResponse)  # With trailing slash
def read_products(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items per page (max 1000)"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search in product name and description"),
    db: Session = Depends(get_db)
):
    try:
        # Calculate skip
        skip = (page - 1) * limit
        
        # Build query
        query = db.query(Product)
        
        # Apply filters
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Product.name.ilike(search_term)) | 
                (Product.description.ilike(search_term))
            )
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        products = query.offset(skip).limit(limit).all()
        
        # Calculate total pages
        total_pages = (total + limit - 1) // limit
        
        return {
            "products": products,
            "total": total,
            "page": page,
            "totalPages": total_pages
        }
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching products: {str(e)}"
        )

@router.get("/{product_id}", response_model=ProductSchema)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("", response_model=ProductSchema)  # Empty string for root path
@router.post("/", response_model=ProductSchema)  # With trailing slash
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin)
):
    # Verify category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update only provided fields
    update_data = product.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_admin)
):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted successfully"}

# Debug endpoints
@router.get("/debug-token")
async def debug_token(authorization: str = Header(None)):
    if not authorization:
        return {"error": "No authorization header provided"}
    
    try:
        # Extract token from header
        token = authorization.replace("Bearer ", "")
        logger.info(f"Received token: {token[:10]}...")  # Log first 10 chars for debugging
        
        # Try to verify with User Service directly
        logger.info("Attempting to connect to User Service...")
        response = requests.get(
            "http://localhost:8001/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        logger.info(f"User Service response: {response.status_code}")
        
        return {
            "token_received": bool(token),
            "token_length": len(token),
            "token_preview": f"{token[:10]}...",  # Show first 10 chars
            "user_service_status": response.status_code,
            "user_service_response": response.text,
            "headers_sent": {"Authorization": "Bearer [token]"}  # Don't log full token
        }
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

@router.get("/test-auth")
async def test_auth(current_user: dict = Depends(verify_token)):
    return {"message": "Token is valid", "user": current_user}

@router.get("/test-admin")
async def test_admin(current_user: dict = Depends(verify_admin)):
    return {"message": "Admin token is valid", "user": current_user} 