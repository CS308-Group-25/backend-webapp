from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(..., max_length=200)
    model: Optional[str] = Field(None, max_length=100)
    serial_no: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    stock: int = Field(0, ge=0)
    warranty: Optional[str] = Field(None, max_length=100)
    distributor: Optional[str] = Field(None, max_length=200)
    brand: Optional[str] = Field(None, max_length=100)
    flavor: Optional[str] = Field(None, max_length=100)
    form: Optional[str] = Field(None, max_length=50)
    serving_size: Optional[str] = Field(None, max_length=50)
    goal_tags: Optional[str] = Field(None, max_length=300)
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    price: Optional[Decimal] = None
    discount: Optional[int] = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
