from pydantic import BaseModel, Field

class AddressCreate(BaseModel):
    customer_id: str
    label: str = "Home"
    address_line: str = Field(min_length=3)
    city: str
    state: str
    pincode: str
    building_society: str | None = None
    latitude: float | None = None
    longitude: float | None = None
