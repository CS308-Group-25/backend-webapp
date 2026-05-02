from datetime import datetime, timezone

from fastapi import HTTPException

from modules.orders.repository import OrderRepository
from modules.refunds.model import RefundRequest
from modules.refunds.repository import RefundRepository
from modules.refunds.schema import AdminRefundRequestResponse


class RefundService:
    def __init__(self, refund_repo: RefundRepository, order_repo: OrderRepository):
        self.refund_repo = refund_repo
        self.order_repo = order_repo

    def request_refund(
        self,
        user_id: int,
        order_id: int,
        order_item_id: int,
        reason: str | None,
    ) -> RefundRequest:
        order = self.order_repo.get_by_order_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access forbidden")

        if order.status != "delivered":
            raise HTTPException(
                status_code=400, detail="Refund only allowed for delivered orders"
            )

        order_item = next(
            (item for item in order.items if item.id == order_item_id), None
        )
        if not order_item or order_item.order_id != order_id:
            raise HTTPException(status_code=404, detail="Order item not found")

        if (datetime.now(timezone.utc) - order.created_at).days > 30:
            raise HTTPException(
                status_code=400, detail="30-day refund window expired"
            )

        if self.refund_repo.get_active_request_for_item(order_item_id):
            raise HTTPException(
                status_code=400,
                detail="A refund request already exists for this item",
            )

        refund_amount = order_item.price * order_item.quantity
        return self.refund_repo.create(order_id, order_item_id, reason, refund_amount)

    def get_admin_refund_requests(
        self, status: str | None = None
    ) -> list[AdminRefundRequestResponse]:
        requests = self.refund_repo.get_all(status)
        return [
            AdminRefundRequestResponse(
                id=r.id,
                customer_name=r.order.user.name,
                product_name=r.order_item.product.name,
                order_date=r.order.created_at,
                refund_amount=r.refund_amount,
                reason=r.reason,
                status=r.status,
            )
            for r in requests
        ]
