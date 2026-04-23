from sqlalchemy import (
    JSON,
    Boolean,
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
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    model = Column(String(100), nullable=True)
    serial_no = Column(String(100), nullable=True, unique=True)
    description = Column(Text, nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    price = Column(Numeric(10, 2), nullable=True)  # sales manager sets this
    warranty = Column(String(100), nullable=True)
    distributor = Column(String(200), nullable=True)

    # --- Supplement-specific & Rich UI fields ---
    brand = Column(String(100), nullable=True)
    flavor = Column(String(100), nullable=True)  # legacy, keep for simple cases
    form = Column(String(50), nullable=True)  # powder / capsule / tablet
    serving_size = Column(String(50), nullable=True)  # legacy
    goal_tags = Column(String(300), nullable=True)  # legacy

    original_price = Column(Numeric(10, 2), nullable=True)
    rating = Column(Numeric(3, 2), nullable=True, default=0)
    review_count = Column(Integer, nullable=True, default=0)
    stock_status = Column(String(20), nullable=True, default="in_stock")
    is_new = Column(Boolean, nullable=True, default=False)

    # JSON columns for the detailed arrays/objects
    images = Column(JSON, nullable=True)
    tags_json = Column(JSON, nullable=True)  # detailed tags list
    flavors_json = Column(JSON, nullable=True)  # [{id, name, color}]
    sizes_json = Column(JSON, nullable=True)  # list of size objects
    features = Column(JSON, nullable=True)  # ["Feature 1", "Feature 2"]
    ingredients = Column(Text, nullable=True)  # Detailed ingredients
    nutrition_facts = Column(JSON, nullable=True)  # [{label, perServing, ...}]
    usage_info = Column(Text, nullable=True)

    # --- Relations ---
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", backref="products")

    # --- Soft delete + timestamps ---
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
