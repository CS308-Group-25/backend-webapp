from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from modules.cart.repository import CartRepository
from modules.cart.schema import (
    CartItemAddRequest,
    CartItemResponse,
    CartItemUpdateRequest,
)
from modules.cart.service import CartService

router = APIRouter(prefix="/api/v1/cart/items", tags=["cart"])


def get_cart_service(db: Session = Depends(get_db)):
    repo = CartRepository(db)
    return CartService(repo, db)


@router.get("", response_model=list[CartItemResponse])
def get_cart_items(user_id: int, service: CartService = Depends(get_cart_service)):
    cart = service.get_cart(user_id)
    return cart.items


@router.post("", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
    user_id: int,
    data: CartItemAddRequest,
    service: CartService = Depends(get_cart_service),
):
    return service.add_item(user_id, data.product_id, data.quantity)


@router.patch("/{cart_item_id}", response_model=CartItemResponse | None)
def update_cart_item(
    cart_item_id: int,
    data: CartItemUpdateRequest,
    service: CartService = Depends(get_cart_service),
):
    return service.update_item(cart_item_id, data.quantity)


@router.delete("/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    cart_item_id: int, service: CartService = Depends(get_cart_service)
):
    success = service.remove_item(cart_item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
        )
    return None
