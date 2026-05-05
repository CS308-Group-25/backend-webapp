from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class InvoiceResponse(BaseModel):
    id: int
    order_id: int
    invoice_number: str
    total: Decimal
    pdf_path: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminInvoiceListItem(BaseModel):
    id: int
    invoice_number: str
    customer_name: str
    total: Decimal
    created_at: datetime


class PaginatedInvoiceResponse(BaseModel):
    items: list[AdminInvoiceListItem]
    total: int
    page: int
    page_size: int
