from datetime import datetime, timezone

from fastapi import HTTPException

from modules.orders.repository import OrderRepository
from modules.products.repository import ProductRepository
from modules.refunds.model import RefundRequest, RefundStatus
from modules.refunds.repository import RefundRepository
from modules.refunds.schema import AdminRefundRequestResponse


class RefundService:
    def __init__(
        self,
        refund_repo: RefundRepository,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
    ):
        self.refund_repo = refund_repo
        self.order_repo = order_repo
        self.product_repo = product_repo

    VALID_TRANSITIONS: dict[RefundStatus, list[RefundStatus]] = {
        RefundStatus.requested: [RefundStatus.approved_waiting_return, 
                                 RefundStatus.rejected],
        RefundStatus.approved_waiting_return: [RefundStatus.returned_received, 
                                               RefundStatus.rejected],
        RefundStatus.returned_received: [RefundStatus.refunded, 
                                         RefundStatus.rejected],
        RefundStatus.rejected: [],
        RefundStatus.refunded: [],
    }

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
            raise HTTPException(status_code=400, detail="30-day refund window expired")

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

    def process_refund_request(
        self, refund_id: int, new_status: RefundStatus
    ) -> AdminRefundRequestResponse:
        refund = self.refund_repo.get_by_id(refund_id)
        if not refund:
            raise HTTPException(status_code=404, detail="Refund request not found")

        current_status = refund.status
        allowed = self.VALID_TRANSITIONS.get(current_status, [])
        if new_status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Invalid status transition from {refund.status} "
                    f"to {new_status.value}"
                ),
            )

        if new_status == RefundStatus.refunded:
            self._restore_stock_and_credit(refund)

        self.refund_repo.update_status(refund, new_status)
        self.refund_repo.db.commit()
        return self._build_admin_response(refund)

    def _restore_stock_and_credit(self, refund: RefundRequest) -> None:
        product = self.product_repo.get_by_id_for_update(refund.order_item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        self.product_repo.update_stock(product.id, -refund.order_item.quantity)

        user = refund.order.user
        user.store_credit = user.store_credit + refund.refund_amount

    def _build_admin_response(
        self, refund: RefundRequest
    ) -> AdminRefundRequestResponse:
        return AdminRefundRequestResponse(
            id=refund.id,
            customer_name=refund.order.user.name,
            product_name=refund.order_item.product.name,
            order_date=refund.order.created_at,
            refund_amount=refund.refund_amount,
            reason=refund.reason,
            status=refund.status,
        )
