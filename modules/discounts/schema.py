from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DiscountCreate(BaseModel):
    product_ids: list[int] = Field(..., min_length=1)
    discount_rate: Decimal = Field(..., gt=0, le=100)


class DiscountRead(BaseModel):
    id: int
    product_ids: list[int]
    discount_rate: Decimal
    original_prices: dict[str, str]
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
