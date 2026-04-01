from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import require_product_manager
from modules.products.schema import ProductCreate, ProductRead
from modules.products.service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_product_manager),
):
    """
    Create a new product. Accessible only by Product Managers.
    """
    service = ProductService(db)
    return service.create_product(product_in)
