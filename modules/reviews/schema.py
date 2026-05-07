from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class ReviewCreate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = None

    @model_validator(mode="after")
    def require_rating_or_comment(self):
        if self.rating is None and not (self.comment and self.comment.strip()):
            raise ValueError("Rating or comment is required")
        return self


class ReviewResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int | None
    comment: str | None
    approval_status: str
    created_at: datetime
    customer_name: Optional[str] = None

    model_config = {"from_attributes": True}


class ReviewAdminResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int | None
    comment: str | None
    approval_status: str
    created_at: datetime
    product_name: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None

    model_config = {"from_attributes": True}


class ReviewModerationRequest(BaseModel):
    approval_status: Literal["approved", "rejected"]
