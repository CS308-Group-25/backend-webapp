from fastapi import HTTPException

from modules.cart.model import Cart, CartItem
from modules.cart.repository import CartRepository
from modules.products.repository import ProductRepository


class CartService:
    def __init__(self, repo: CartRepository, product_repo: ProductRepository):
        self.repo = repo
        self.product_repo = product_repo

    def get_cart(self, user_id: int) -> Cart | None:
        cart = self.repo.get(user_id)
        if not cart:
            cart = self.repo.create(user_id)
        return cart

    def add_item(self, user_id: int, product_id: int, quantity: int = 1) -> CartItem:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.stock < quantity:
            raise HTTPException(status_code=400, detail="Not enough stock")

        cart = self.get_cart(user_id)
        return self.repo.add_item(cart.id, product.id, quantity)

    def verify_item_ownership(self, cart_item_id: int, user_id: int) -> None:
        cart_item = self.repo.get_item_by_id(cart_item_id)
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        cart = self.repo.get(user_id)
        if not cart or cart_item.cart_id != cart.id:
            raise HTTPException(
                status_code=403, detail="This cart item does not belong to you"
            )

    def update_item(self, cart_item_id: int, quantity: int) -> CartItem | None:
        if quantity <= 0:
            self.repo.remove_item(cart_item_id)
            return None
        return self.repo.update_item(cart_item_id, quantity)

    def remove_item(self, cart_item_id: int) -> bool:
        return self.repo.remove_item(cart_item_id)
