from pydantic import BaseModel, Field
class AuditRecord(BaseModel):
    action: str = Field(min_length=2)
    entity_type: str = Field(min_length=2)
    entity_id: str | None = None
    old_values: dict | None = None
    new_values: dict | None = None
    device_id: str | None = None
