from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import require_product_manager
from modules.products.repository import ProductRepository
from modules.products.schema import (
    ProductCreate,
    ProductDetailResponse,
    ProductListResponse,
    ProductRead,
    ProductUpdate,
)
from modules.products.service import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["products"])
admin_router = APIRouter(prefix="/api/v1/admin/products", tags=["admin-products"])


@router.get("", response_model=list[ProductListResponse])
def list_products(db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    service = ProductService(repo)

    return service.list_products()

@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    service = ProductService(repo)

    return service.get_product(product_id)

@admin_router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_product_manager),
):
    repo = ProductRepository(db)
    service = ProductService(repo)

    return service.create_product(product_in)

@admin_router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_product_manager),
):
    repo = ProductRepository(db)
    service = ProductService(repo)

    return service.update_product(product_id, product_in)

@admin_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_product_manager),
):
    repo = ProductRepository(db)
    service = ProductService(repo)

    service.delete_product(product_id)