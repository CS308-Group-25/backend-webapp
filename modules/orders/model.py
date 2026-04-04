from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=True)
    delivery_address = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    total_price = Column(Numeric(10,2), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False)
    user = relationship("User", backref="orders")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)     # snapshot at order time

    order = relationship("Order", back_populates="items")
    product = relationship("Product", backref="order_items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    card_last4 = Column(String(4), nullable=False)
    card_brand = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="success")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="payment")

