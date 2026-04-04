from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,  # noqa: E402, F401
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class Product(Base):
    __tablename__ = "products"
    # --- Course-required fields ---
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(200), nullable=False)
    model       = Column(String(100), nullable=True)
    serial_no   = Column(String(100), nullable=True, unique=True)
    description = Column(Text, nullable=True)
    stock       = Column(Integer, nullable=False, default=0)
    price       = Column(Numeric(10, 2), nullable=True)   # sales manager sets this
    warranty    = Column(String(100), nullable=True)
    distributor = Column(String(200), nullable=True)

    # --- Supplement-specific fields ---
    brand        = Column(String(100), nullable=True)
    flavor       = Column(String(100), nullable=True)
    form         = Column(String(50),  nullable=True)   # powder / capsule / tablet
    serving_size = Column(String(50),  nullable=True)
    goal_tags    = Column(String(300), nullable=True)   # e.g. "muscle gain,recovery"

    # --- Relations ---
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category    = relationship("Category", backref="products")

    # --- Soft delete + timestamps ---
    deleted_at  = Column(DateTime(timezone=True), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())