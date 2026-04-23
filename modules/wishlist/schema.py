from datetime import datetime

from pydantic import BaseModel


class WishlistAddRequest(BaseModel):
    """Request body for adding a product to the wishlist."""

    product_id: int


class WishlistItemResponse(BaseModel):
    """Response schema for a single wishlist item."""

    id: int
    user_id: int
    product_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
