from pydantic import BaseModel


class AddressCreate(BaseModel):
    title: str = ""
    first_name: str
    last_name: str
    address: str
    apartment: str = ""
    city: str
    district: str
    phone: str


class AddressResponse(BaseModel):
    id: int
    title: str
    first_name: str
    last_name: str
    address: str
    apartment: str | None
    city: str
    district: str
    phone: str

    model_config = {"from_attributes": True}
