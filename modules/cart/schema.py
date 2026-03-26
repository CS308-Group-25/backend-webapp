from pydantic import BaseModel


class CartItemAddRequest(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdateRequest(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: list[CartItemResponse] = []

    model_config = {"from_attributes": True}
