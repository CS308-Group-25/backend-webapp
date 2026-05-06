import os
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user, require_sales_manager
from modules.auth.model import User
from modules.invoices.repository import InvoiceRepository
from modules.invoices.schema import InvoiceResponse, PaginatedInvoiceResponse
from modules.invoices.service import InvoiceService
from modules.orders.repository import OrderRepository

router = APIRouter(prefix="/api/v1/orders", tags=["invoices"])
admin_router = APIRouter(prefix="/api/v1/admin/invoices", tags=["admin-invoices"])


@router.get(
    "/{order_id}/invoice",
    response_model=InvoiceResponse,
    status_code=status.HTTP_200_OK,
)
def get_invoice(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order_repo = OrderRepository(db)
    order = order_repo.get_by_order_id(order_id)
    if order is None:
        raise HTTPException(404, detail="Order does not exist.")
    if order.user_id != current_user.id:
        raise HTTPException(403, detail="Order does not belong this user.")

    invoice_repo = InvoiceRepository(db)
    invoice_service = InvoiceService(invoice_repo)
    invoice = invoice_service.get_by_order_id(order.id)
    return invoice


@admin_router.get("", response_model=PaginatedInvoiceResponse)
def list_invoices(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_sales_manager),
    db: Session = Depends(get_db),
):
    invoice_repo = InvoiceRepository(db)
    invoice_service = InvoiceService(invoice_repo)
    items, total = invoice_service.list_admin(from_date, to_date, page, page_size)
    return PaginatedInvoiceResponse(items, total, page, page_size)


@admin_router.get("/{invoice_id}/pdf")
def get_invoice_pdf(
    invoice_id: int,
    current_user: User = Depends(require_sales_manager),
    db: Session = Depends(get_db),
):
    invoice_repo = InvoiceRepository(db)
    invoice_service = InvoiceService(invoice_repo)
    invoice = invoice_service.get_by_id(invoice_id)
    if invoice is None:
        raise HTTPException(404, detail="Invoice not found.")
    if not invoice.pdf_path or not os.path.exists(invoice.pdf_path):
        raise HTTPException(404, detail="PDF file not found.")
    return FileResponse(
        invoice.pdf_path,
        media_type="application/pdf",
        filename=f"{invoice.invoice_number}.pdf",
    )
