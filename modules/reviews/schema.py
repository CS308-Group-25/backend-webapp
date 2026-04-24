from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None


class ReviewResponse(BaseModel):
    id: int
    product_id: int
    user_id: int
    rating: int
    comment: str | None
    approval_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewModerationRequest(BaseModel):
    approval_status: Literal["approved", "rejected"]
