from sqlalchemy.orm import Session

from modules.auth.model import User
from modules.wishlist.model import WishlistItem


class WishlistRepository:
    """Handles all database operations for wishlist items."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_user(self, user_id: int) -> list[WishlistItem]:
        """Return all wishlist items belonging to the given user."""
        return (
            self.db.query(WishlistItem)
            .filter(WishlistItem.user_id == user_id)
            .all()
        )

    def get_item(self, user_id: int, product_id: int) -> WishlistItem | None:
        """Return a specific wishlist item, or None if it doesn't exist.

        Used internally for duplicate checks and delete lookups.
        """
        return (
            self.db.query(WishlistItem)
            .filter(
                WishlistItem.user_id == user_id,
                WishlistItem.product_id == product_id,
            )
            .first()
        )

    def get_users_by_product(self, product_id: int) -> list[User]:
        """Return all users who have the given product in their wishlist.

        Used to find notification recipients when a product's price drops.
        """
        return (
            self.db.query(User)
            .join(WishlistItem, WishlistItem.user_id == User.id)
            .filter(WishlistItem.product_id == product_id)
            .all()
        )

    def add(self, user_id: int, product_id: int) -> WishlistItem:
        """Create and persist a new wishlist item for the given user and product."""
        item = WishlistItem(user_id=user_id, product_id=product_id)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def remove(self, user_id: int, product_id: int) -> bool:
        """Delete a wishlist item. Returns True if deleted, False if not found."""
        item = self.get_item(user_id, product_id)
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False
