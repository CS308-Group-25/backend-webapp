from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class SubCategoryBase(BaseModel):
    name: str
    description: str | None = None

class SubCategoryCreate(SubCategoryBase):
    category_id: int

class SubCategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None

class SubCategoryResponse(SubCategoryBase):
    id: int
    category_id: int

    model_config = {"from_attributes": True}

class SubCategoryListResponse(SubCategoryResponse):
    categoryName: str
    productCount: int
