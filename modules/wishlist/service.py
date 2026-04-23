from fastapi import HTTPException

from modules.products.repository import ProductRepository
from modules.wishlist.model import WishlistItem
from modules.wishlist.repository import WishlistRepository


class WishlistService:
    """Business logic layer for wishlist operations."""

    def __init__(self, repo: WishlistRepository, product_repo: ProductRepository):
        self.repo = repo
        self.product_repo = product_repo

    def get_by_user(self, user_id: int) -> list[WishlistItem]:
        """Return all wishlist items for the given user."""
        return self.repo.get_by_user(user_id)

    def add(self, user_id: int, product_id: int) -> WishlistItem:
        """Add a product to the user's wishlist.

        Raises:
            404 if the product does not exist.
            409 if the product is already in the wishlist.
        """
        # Ensure the product exists before adding it 
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Prevent duplicate entries (DB UniqueConstraint is the last line of defence)
        existing = self.repo.get_item(user_id, product_id)
        if existing:
            raise HTTPException(
                status_code=409, detail="Product already in wishlist"
            )

        return self.repo.add(user_id, product_id)

    def remove(self, user_id: int, product_id: int) -> None:
        """Remove a product from the user's wishlist.

        Raises:
            404 if the product is not in the wishlist.
        """
        removed = self.repo.remove(user_id, product_id)
        if not removed:
            raise HTTPException(
                status_code=404, detail="Product not found in wishlist"
            )
