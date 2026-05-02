from sqlalchemy import (
  CheckConstraint,
  Column,
  DateTime,
  ForeignKey,
  Integer,
  String,
  Text,
)
from sqlalchemy.sql import func

from core.database import Base


class Review(Base):
  __tablename__ ="reviews"
  id= Column(Integer, primary_key=True, index=True)
  product_id = Column(Integer, ForeignKey("products.id"),nullable=False, index=True)
  user_id = Column(Integer, ForeignKey("users.id"), nullable=False,index=True)
  rating = Column(Integer, nullable= False)
  comment = Column(Text, nullable=True)
  approval_status = Column(String(20), nullable=False, default="pending")
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  __table_args__ = (
    CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating"),
  )
