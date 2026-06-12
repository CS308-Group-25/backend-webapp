from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import (
    require_admin,
    require_product_manager,
    require_sales_manager,
)
from modules.discounts.repository import DiscountRepository
from modules.products.repository import ProductRepository
from modules.products.schema import (
    PaginatedProductResponse,
    ProductCreate,
    ProductDetailResponse,
    ProductPriceUpdate,
    ProductRead,
    ProductUpdate,
)
from modules.products.service import ProductService
from modules.notifications.repository import NotificationRepository
from modules.wishlist.repository import WishlistRepository

router = APIRouter(prefix="/api/v1/products", tags=["products"])
admin_router = APIRouter(prefix="/api/v1/admin/products", tags=["admin-products"])


@router.get("", response_model=PaginatedProductResponse)
def list_products(
    search: str | None = None,
    sort: str | None = None,
    category_id: int | None = None,
    brand: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):

    repo = ProductRepository(db)
    service = ProductService(repo)
    items, total = service.list_products(
        search=search,
        sort=sort,
        category_id=category_id,
        brand=brand,
        page=page,
        page_size=page_size,
    )

    return PaginatedProductResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    service = ProductService(repo)

    return service.get_product(product_id)


@admin_router.get("", response_model=PaginatedProductResponse)
def list_admin_products(
    page: int = 1,
    page_size: int = 1000,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Admin product listing — includes unpriced drafts invisible to customers."""
    repo = ProductRepository(db)
    service = ProductService(repo)
    items, total = service.list_all_admin(page=page, page_size=page_size)
    return PaginatedProductResponse(
        items=items, total=total, page=page, page_size=page_size
    )


@admin_router.get("/{product_id}", response_model=ProductDetailResponse)
def get_admin_product(
    product_id: int, 
    db: Session = Depends(get_db),
    _: None = Depends(require_product_manager),
):
    repo = ProductRepository(db)
    service = ProductService(repo)
    return service.get_admin_product(product_id)


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


@admin_router.patch("/{product_id}/price", response_model=ProductRead)
def set_product_price(
    product_id: int,
    price_in: ProductPriceUpdate,
    db: Session = Depends(get_db),
    _: None = Depends(require_sales_manager),
):
    repo = ProductRepository(db)
    service = ProductService(repo, discount_repo=DiscountRepository(db))

    old_price = repo.get_by_id(product_id)
    old_price_val = float(old_price.price) if old_price and old_price.price is not None else None
    updated = service.set_price(product_id, price_in.price)

    if old_price_val is not None and float(price_in.price) < old_price_val:
        wishlist_repo = WishlistRepository(db)
        notif_repo = NotificationRepository(db)
        wishlisted_users = wishlist_repo.get_users_by_product(product_id)
        for user in wishlisted_users:
            notif_repo.create(
                user.id,
                f"Favori listenizde bulunan '{updated.name}' ürününün fiyatı düştü! Yeni fiyat: {float(price_in.price):.2f} TL",
            )
        db.commit()

    return updated