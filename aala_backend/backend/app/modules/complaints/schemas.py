from pydantic import BaseModel, Field
class ComplaintCreate(BaseModel):
    order_id: str; customer_id: str; category: str; description: str = Field(min_length=3)
    evidence_urls: list[str] = Field(default_factory=list)
class ComplaintStatusUpdate(BaseModel):
    status: str = Field(pattern='^(ASSIGNED|UNDER_INVESTIGATION|ACTION_REQUIRED|RESOLVED|CLOSED|REJECTED)$')
    remarks: str | None=None; assigned_to: str | None=None
