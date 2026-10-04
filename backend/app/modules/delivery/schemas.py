from pydantic import BaseModel, Field

class DeliveryAssign(BaseModel): partner_id: str
class DeliveryStart(BaseModel): partner_id: str
class DeliveryConfirm(BaseModel):
    delivery_code: str = Field(min_length=4,max_length=20)
    receiver_name: str = Field(min_length=1,max_length=150)
    receiver_mobile: str | None = Field(default=None,max_length=30)
    latitude: float = Field(ge=-90,le=90)
    longitude: float = Field(ge=-180,le=180)
    remarks: str | None = None
class DeliveryException(BaseModel):
    reason: str = Field(min_length=3)
    receiver_name: str = Field(min_length=1,max_length=150)
    receiver_mobile: str = Field(min_length=1,max_length=30)
    evidence_url: str = Field(min_length=1)
    house_number: str | None = Field(default=None,max_length=100)
    latitude: float = Field(ge=-90,le=90)
    longitude: float = Field(ge=-180,le=180)
    remarks: str | None = None
