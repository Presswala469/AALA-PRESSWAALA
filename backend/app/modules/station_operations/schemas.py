from pydantic import BaseModel, Field

class StationArrival(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    arrived_at: str | None = None

class StationReceive(BaseModel):
    partner_handover_quantity: int = Field(ge=0)
    station_received_quantity: int = Field(ge=0)
    reason: str | None = None
    remarks: str | None = None

class StationStatusUpdate(BaseModel):
    status: str
    reason: str | None = None
    remarks: str | None = None

class StationEvidence(BaseModel):
    evidence_url: str
    evidence_type: str = "photo"
    remarks: str | None = None
