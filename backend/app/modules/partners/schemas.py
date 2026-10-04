from pydantic import BaseModel, Field
class PartnerCreate(BaseModel):
    employee_id: str = Field(min_length=2, max_length=60)
    name: str = Field(min_length=2, max_length=150)
    mobile_number: str = Field(min_length=5, max_length=30)
    station_code: str | None = None
    active: bool = True
class PartnerOut(PartnerCreate):
    partner_id: str
class PartnerAssign(BaseModel):
    partner_id: str
    station_code: str | None = None
class PickupArrival(BaseModel):
    latitude: float
    longitude: float
    arrived_at: str | None = None
class GarmentVerification(BaseModel):
    handover_quantity: int = Field(ge=0)
    customer_confirmed: bool = False
    notes: str | None = None
class DamageEvidence(BaseModel):
    item_ref: str
    photo_url: str
    description: str | None = None
class BagAssignment(BaseModel):
    bag_id: str
class PickupComplete(BaseModel):
    received_quantity: int = Field(ge=0)
    customer_confirmed: bool = False
    notes: str | None = None
