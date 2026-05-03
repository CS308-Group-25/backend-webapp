from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import require_sales_manager
from modules.auth.model import User
from modules.discounts.repository import DiscountRepository
from modules.discounts.schema import DiscountCreate, DiscountRead
from modules.discounts.service import DiscountService
from modules.products.repository import ProductRepository
from modules.wishlist.repository import WishlistRepository

router = APIRouter(prefix="/api/v1/admin/discounts", tags=["admin-discounts"])


@router.post("", response_model=DiscountRead, status_code=status.HTTP_201_CREATED)
def create_discount(
    discount_in: DiscountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_sales_manager),
):
    service = DiscountService(
        DiscountRepository(db),
        ProductRepository(db),
        WishlistRepository(db),
    )
    return service.apply_discount(
        product_ids=discount_in.product_ids,
        discount_rate=discount_in.discount_rate,
        created_by=current_user.id,
    )


@router.delete("/{discount_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_discount(
    discount_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_sales_manager),
):
    service = DiscountService(
        DiscountRepository(db),
        ProductRepository(db),
        WishlistRepository(db),
    )
    service.remove_discount(discount_id)
