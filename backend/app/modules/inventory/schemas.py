from pydantic import BaseModel, Field

class InventoryCreate(BaseModel):
    item_type: str = Field(min_length=2, max_length=30)
    item_code: str | None = None
    holder_type: str | None = None
    holder_id: str | None = None
    location: str | None = None
    remarks: str | None = None

class InventoryUpdate(BaseModel):
    status: str = Field(min_length=2, max_length=30)
    holder_type: str | None = None
    holder_id: str | None = None
    location: str | None = None
    remarks: str | None = None
    evidence_url: str | None = None

class InventoryOut(InventoryCreate):
    inventory_id: str
    status: str
    created_at: str

class InventoryAdjustment(BaseModel):
    action: str = Field(min_length=2, max_length=30)
    remarks: str = Field(min_length=2)
    evidence_url: str | None = None
