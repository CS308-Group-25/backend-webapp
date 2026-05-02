import enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class RefundStatus(str, enum.Enum):
    requested = "requested"
    approved_waiting_return = "approved_waiting_return"
    returned_received = "returned_received"
    refunded = "refunded"
    rejected = "rejected"


class RefundRequest(Base):
    __tablename__ = "refund_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    order_item_id = Column(
        Integer, ForeignKey("order_items.id"), nullable=False, index=True
    )
    status = Column(String(30), nullable=False, default=RefundStatus.requested)
    reason = Column(String, nullable=True)
    refund_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    order = relationship("Order", backref="refund_requests")
    order_item = relationship("OrderItem", backref="refund_requests")
