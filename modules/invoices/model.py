from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, unique=True)
    invoice_number = Column(String(20), nullable=False, unique=True)    # TODO: invoice number T-134     # noqa: E501
    total = Column(Numeric(10,2), nullable=False)
    pdf_path = Column(String(500), nullable=True)       # TODO: pdf will be done in T-134   # noqa: E501
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="invoice")