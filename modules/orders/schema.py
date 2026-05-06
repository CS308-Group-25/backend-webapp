from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict

from modules.refunds.schema import RefundRequestSummary


class OrderRequest(BaseModel):
    delivery_address: str
    card_number: str
    card_last4: str
    card_brand: str


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    product_id: int
    name: str
    quantity: int
    price: Decimal
    variant_name: str | None = None
    refund_request: RefundRequestSummary | None = None


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    total: Decimal
    invoice_id: int | None = None  # Made nullable until invoice tasks are done
    items: List[OrderItemResponse]
    delivery_address: str
    created_at: datetime


class AdminOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    order_id: int
    customer_id: int
    total: Decimal
    items: List[OrderItemResponse]
    delivery_address: str
    status: str
    completed: bool
    customer_name: str
    customer_email: str


class StatusUpdateRequest(BaseModel):
    status: str
