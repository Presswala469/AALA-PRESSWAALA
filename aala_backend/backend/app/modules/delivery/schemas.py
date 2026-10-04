from pydantic import BaseModel, Field
class DeliveryAssign(BaseModel): partner_id: str
class DeliveryStart(BaseModel): partner_id: str
class DeliveryConfirm(BaseModel): delivery_code: str = Field(min_length=4,max_length=20); receiver_name: str | None = None; latitude: float | None = None; longitude: float | None = None; evidence_url: str | None = None
class DeliveryException(BaseModel): reason: str = Field(min_length=3); receiver_name: str | None = None; evidence_url: str | None = None; remarks: str | None = None
