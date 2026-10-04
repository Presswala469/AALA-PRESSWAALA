from pydantic import BaseModel, Field

class SupportRequestCreate(BaseModel):
    station_code: str
    order_id: str | None = None
    request_type: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=3)
    priority: str = Field(default='NORMAL', pattern='^(LOW|NORMAL|HIGH|URGENT)$')

class SupportStatusUpdate(BaseModel):
    status: str = Field(pattern='^(OPEN|IN_PROGRESS|RESOLVED|CLOSED)$')
