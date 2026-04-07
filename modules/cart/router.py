from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from modules.auth.model import User
from modules.cart.repository import CartRepository
from modules.cart.schema import (
    CartItemAddRequest,
    CartItemResponse,
    CartItemUpdateRequest,
)
from modules.cart.service import CartService
from modules.products.repository import ProductRepository

router = APIRouter(prefix="/api/v1/cart/items", tags=["cart"])


def get_cart_service(db: Session = Depends(get_db)):
    repo = CartRepository(db)
    product_repo = ProductRepository(db)
    return CartService(repo, product_repo)


@router.get("", response_model=list[CartItemResponse])
def get_cart_items(
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    cart = service.get_cart(current_user.id)
    return cart.items


@router.post("", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
    data: CartItemAddRequest,
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    return service.add_item(current_user.id, data.product_id, data.quantity)


@router.patch("/{cart_item_id}", response_model=CartItemResponse | None)
def update_cart_item(
    cart_item_id: int,
    data: CartItemUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    service.verify_item_ownership(cart_item_id, current_user.id)
    return service.update_item(cart_item_id, data.quantity)


@router.delete("/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    cart_item_id: int,
    current_user: User = Depends(get_current_user),
    service: CartService = Depends(get_cart_service),
):
    service.verify_item_ownership(cart_item_id, current_user.id)
    success = service.remove_item(cart_item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
        )
    return None
