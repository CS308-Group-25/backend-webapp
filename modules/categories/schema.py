from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = {"from_attributes": True}