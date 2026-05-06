from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    name: str = Field(..., max_length=200)
    model: Optional[str] = Field(None, max_length=100)
    serial_no: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    stock: int = Field(0, ge=0)
    warranty: Optional[str] = Field(None, max_length=100)
    distributor: Optional[str] = Field(None, max_length=200)
    brand: Optional[str] = Field(None, max_length=100)
    sub_type: Optional[str] = Field(None, max_length=100)
    flavor: Optional[str] = Field(None, max_length=100)
    form: Optional[str] = Field(None, max_length=50)
    serving_size: Optional[str] = Field(None, max_length=50)
    goal_tags: Optional[str] = Field(None, max_length=300)
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    model: Optional[str] = Field(None, max_length=100)
    serial_no: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    warranty: Optional[str] = Field(None, max_length=100)
    distributor: Optional[str] = Field(None, max_length=200)
    brand: Optional[str] = Field(None, max_length=100)
    sub_type: Optional[str] = Field(None, max_length=100)
    flavor: Optional[str] = Field(None, max_length=100)
    form: Optional[str] = Field(None, max_length=50)
    serving_size: Optional[str] = Field(None, max_length=50)
    goal_tags: Optional[str] = Field(None, max_length=300)
    category_id: Optional[int] = None


class ProductRead(ProductBase):
    id: int
    price: Optional[Decimal] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float | None
    original_price: float | None
    stock: int
    stock_status: str | None
    is_new: bool | None
    rating: float | None
    review_count: int | None
    brand: str | None
    sub_type: str | None
    flavor: str | None
    form: str | None
    goal_tags: str | None
    images: list[str] | None
    tags_json: list[str] | None
    category: CategoryResponse | None

    model_config = {"from_attributes": True}


class ProductDetailResponse(BaseModel):
    id: int
    name: str
    model: str | None
    serial_no: str | None
    description: str | None
    stock: int
    price: float | None
    original_price: float | None
    rating: float | None
    review_count: int | None
    stock_status: str | None
    is_new: bool | None
    warranty: str | None
    distributor: str | None
    brand: str | None
    sub_type: str | None
    flavor: str | None
    form: str | None
    serving_size: str | None
    goal_tags: str | None
    images: list[str] | None
    tags_json: list[str] | None
    flavors_json: list[Any] | None
    sizes_json: list[Any] | None
    features: list[str] | None
    ingredients: str | None
    nutrition_facts: list[Any] | None
    usage_info: str | None
    category: CategoryResponse | None

    model_config = {"from_attributes": True}


class PaginatedProductResponse(BaseModel):
    items: list[ProductListResponse]
    total: int
    page: int
    page_size: int


class ProductPriceUpdate(BaseModel):
    price: Decimal = Field(..., gt=0)
