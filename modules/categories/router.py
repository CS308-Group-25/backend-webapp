from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import require_product_manager
from modules.categories.repository import CategoryRepository
from modules.categories.schema import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from modules.categories.service import CategoryService

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])
admin_router = APIRouter(prefix="/api/v1/admin/categories", tags=["admin-categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    service = CategoryService(repo)

    return service.list_categories()


@admin_router.post(
    "", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _: None = Depends(require_product_manager),
):
    repo = CategoryRepository(db)
    service = CategoryService(repo)
    return service.create_category(data)


@admin_router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_product_manager),
):
    repo = CategoryRepository(db)
    service = CategoryService(repo)
    return service.update_category(category_id, data)


@admin_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_product_manager),
):
    repo = CategoryRepository(db)
    service = CategoryService(repo)
    service.delete_category(category_id)
