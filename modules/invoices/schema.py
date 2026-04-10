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
