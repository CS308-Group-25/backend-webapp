from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from modules.auth.model import User
from modules.products.repository import ProductRepository
from modules.wishlist.repository import WishlistRepository
from modules.wishlist.schema import WishlistAddRequest, WishlistItemResponse
from modules.wishlist.service import WishlistService

router = APIRouter(prefix="/api/v1/wishlist/items", tags=["wishlist"])


def get_wishlist_service(db: Session = Depends(get_db)) -> WishlistService:
    """Dependency: build WishlistService with its required repositories."""
    repo = WishlistRepository(db)
    product_repo = ProductRepository(db)
    return WishlistService(repo, product_repo)


@router.get("", response_model=list[WishlistItemResponse])
def get_wishlist(
    current_user: User = Depends(get_current_user),
    service: WishlistService = Depends(get_wishlist_service),
):
    """Return all wishlist items for the authenticated user."""
    return service.get_by_user(current_user.id)


@router.post(
    "",
    response_model=WishlistItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_to_wishlist(
    data: WishlistAddRequest,
    current_user: User = Depends(get_current_user),
    service: WishlistService = Depends(get_wishlist_service),
):
    """Add a product to the authenticated user's wishlist."""
    return service.add(current_user.id, data.product_id)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    service: WishlistService = Depends(get_wishlist_service),
):
    """Remove a product from the authenticated user's wishlist."""
    service.remove(current_user.id, product_id)
    return None
