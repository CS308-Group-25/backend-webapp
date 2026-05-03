from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.sql import func

from core.database import Base


class Discount(Base):
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, index=True)
    product_ids = Column(JSON, nullable=False)
    discount_rate = Column(Numeric(5, 2), nullable=False)
    original_prices = Column(JSON, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
