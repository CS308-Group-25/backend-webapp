from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class WishlistItem(Base):
    """Represents a single product saved to a user's wishlist."""

    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, index=True)
    # FK to the user who owns this wishlist entry
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    # FK to the saved product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )

    # Allows wishlist_item.product to load the full Product object
    product = relationship("Product")

    __table_args__ = (
        # Prevent the same product from being added twice by the same user
        UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
    )
