from decimal import Decimal

from sqlalchemy.orm import Session

from modules.refunds.model import RefundRequest, RefundStatus


class RefundRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        order_id: int,
        order_item_id: int,
        reason: str | None,
        refund_amount: Decimal,
    ) -> RefundRequest:
        refund = RefundRequest(
            order_id=order_id,
            order_item_id=order_item_id,
            reason=reason,
            refund_amount=refund_amount,
            status=RefundStatus.requested,
        )
        self.db.add(refund)
        self.db.commit()
        self.db.refresh(refund)
        return refund

    def get_active_request_for_item(self, order_item_id: int) -> RefundRequest | None:
        return (
            self.db.query(RefundRequest)
            .filter(
                RefundRequest.order_item_id == order_item_id,
                RefundRequest.status != RefundStatus.rejected,
            )
            .first()
        )

    def get_by_order_item(self, order_item_id: int) -> RefundRequest | None:
        return (
            self.db.query(RefundRequest)
            .filter(RefundRequest.order_item_id == order_item_id)
            .order_by(RefundRequest.created_at.desc())
            .first()
        )
