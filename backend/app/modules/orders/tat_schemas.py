from pydantic import BaseModel, Field
class TATRuleCreate(BaseModel):
    service_code: str
    target_minutes: int = Field(gt=0)
    urgent_threshold_minutes: int = Field(default=60, ge=0)
class TATRuleOut(TATRuleCreate):
    active: bool
