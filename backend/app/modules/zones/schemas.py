from pydantic import BaseModel, Field
class ZoneCreate(BaseModel):
    zone_code: str = Field(min_length=1,max_length=60)
    name: str = Field(min_length=1,max_length=120)
    city: str | None = None
    active: bool = True
class ZoneAssignmentCreate(BaseModel):
    user_id: str
    zone_id: str
    active: bool = True
