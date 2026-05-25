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


class AdminInvoiceItem(BaseModel):
    product_id: int
    name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class AdminInvoiceListItem(BaseModel):
    id: int
    order_id: int
    invoice_number: str
    customer_name: str
    customer_email: str
    delivery_address: str
    payment_method: str
    total: Decimal
    created_at: datetime
    items: list[AdminInvoiceItem]
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal


class PaginatedInvoiceResponse(BaseModel):
    items: list[AdminInvoiceListItem]
    total: int
    page: int
    page_size: int
