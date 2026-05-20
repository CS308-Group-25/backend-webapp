from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from modules.orders.model import Order, OrderItem
from modules.refunds.model import RefundRequest, RefundStatus


class ReportsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_revenue_by_date(
        self, from_date: date, to_date: date
    ) -> list[tuple[date, Decimal]]:
        refunded_item_ids = (
            self.db.query(RefundRequest.order_item_id)
            .filter(RefundRequest.status == RefundStatus.refunded)
            .subquery()
        )

        rows = (
            self.db.query(
                func.date(Order.created_at).label("day"),
                func.sum(OrderItem.price * OrderItem.quantity).label("revenue"),
            )
            .join(OrderItem, OrderItem.order_id == Order.id)
            .filter(
                func.date(Order.created_at) >= from_date,
                func.date(Order.created_at) <= to_date,
                Order.status != "cancelled",
                ~OrderItem.id.in_(refunded_item_ids),
            )
            .group_by(func.date(Order.created_at))
            .order_by(func.date(Order.created_at))
            .all()
        )

        return [(row.day, Decimal(str(row.revenue))) for row in rows]