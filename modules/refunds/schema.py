from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class RefundRequestCreate(BaseModel):
    reason: str | None = None


class RefundRequestResponse(BaseModel):
    id: int
    order_id: int
    order_item_id: int
    status: str
    reason: str | None
    refund_amount: Decimal
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RefundRequestSummary(BaseModel):
    id: int
    status: str
    refund_amount: Decimal
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
