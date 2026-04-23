from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from modules.auth.model import User
from modules.invoices.repository import InvoiceRepository
from modules.invoices.schema import InvoiceResponse
from modules.invoices.service import InvoiceService
from modules.orders.repository import OrderRepository

router = APIRouter(prefix="/api/v1/orders", tags=["invoices"])


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
