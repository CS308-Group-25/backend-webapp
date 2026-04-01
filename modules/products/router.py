from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from modules.auth.model import User
from modules.products.model import Product
from modules.products.schema import ProductCreate, ProductRead

router = APIRouter(prefix="/products", tags=["products"])


def require_product_manager(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "product_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only product managers can perform this action",
        )
    return current_user


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_product_manager),
):
    """
    Create a new product. Accessible only by Product Managers.
    """
    # Create product instance from schema
    product_data = product_in.model_dump()
    db_product = Product(**product_data)
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product
