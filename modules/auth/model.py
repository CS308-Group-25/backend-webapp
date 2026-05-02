from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    tax_id = Column(String, nullable=True)
    address = Column(String, nullable=True)
    role = Column(String, nullable=False, default="customer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
