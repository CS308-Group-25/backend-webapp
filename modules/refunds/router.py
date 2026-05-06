from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user, require_sales_manager
from modules.auth.model import User
from modules.orders.repository import OrderRepository
from modules.products.repository import ProductRepository
from modules.refunds.model import RefundStatus
from modules.refunds.repository import RefundRepository
from modules.refunds.schema import (
    AdminRefundRequestResponse,
    RefundRequestCreate,
    RefundRequestResponse,
    RefundStatusUpdate,
)
from modules.refunds.service import RefundService

router = APIRouter(prefix="/api/v1", tags=["refunds"])
admin_router = APIRouter(prefix="/api/v1/admin/refund-requests", tags=["admin-refunds"])


@router.post(
    "/orders/{order_id}/items/{item_id}/refund-requests",
    response_model=RefundRequestResponse,
    status_code=201,
)
def request_refund(
    order_id: int,
    item_id: int,
    payload: RefundRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    refund_repo = RefundRepository(db)
    order_repo = OrderRepository(db)
    product_repo = ProductRepository(db)
    service = RefundService(refund_repo, order_repo, product_repo)
    return service.request_refund(
        user_id=current_user.id,
        order_id=order_id,
        order_item_id=item_id,
        reason=payload.reason,
    )


@admin_router.get(
    "", response_model=list[AdminRefundRequestResponse], status_code=200
)
def get_admin_refund_requests(
    status: RefundStatus | None = None,
    current_user: User = Depends(require_sales_manager),
    db: Session = Depends(get_db),
):
    refund_repo = RefundRepository(db)
    order_repo = OrderRepository(db)
    product_repo = ProductRepository(db)
    service = RefundService(refund_repo, order_repo, product_repo)
    return service.get_admin_refund_requests(status)


@admin_router.patch(
    "/{refund_id}",
    response_model=AdminRefundRequestResponse,
    status_code=200,
)
def update_refund_request(
    refund_id: int,
    data: RefundStatusUpdate,
    current_user: User = Depends(require_sales_manager),
    db: Session = Depends(get_db),
):
    refund_repo = RefundRepository(db)
    order_repo = OrderRepository(db)
    product_repo = ProductRepository(db)
    service = RefundService(refund_repo, order_repo, product_repo)
    return service.process_refund_request(refund_id, data.status)
