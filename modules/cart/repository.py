from sqlalchemy.orm import Session

from modules.cart.model import Cart, CartItem


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_id: int) -> Cart | None:
        return self.db.query(Cart).filter(Cart.user_id == user_id).first()

    def create(self, user_id: int) -> Cart:
        cart = Cart(user_id=user_id)
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def add_item(self, cart_id: int, product_id: int, quantity: int = 1) -> CartItem:
        cart_item = (
            self.db.query(CartItem)
            .filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
            .first()
        )
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(
                cart_id=cart_id, product_id=product_id, quantity=quantity
            )
            self.db.add(cart_item)

        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item

    def update_item(self, cart_item_id: int, quantity: int) -> CartItem | None:
        cart_item = self.db.query(CartItem).filter(CartItem.id == cart_item_id).first()
        if cart_item:
            cart_item.quantity = quantity
            self.db.commit()
            self.db.refresh(cart_item)
        return cart_item

    def remove_item(self, cart_item_id: int) -> bool:
        cart_item = self.db.query(CartItem).filter(CartItem.id == cart_item_id).first()
        if cart_item:
            self.db.delete(cart_item)
            self.db.commit()
            return True
        return False
