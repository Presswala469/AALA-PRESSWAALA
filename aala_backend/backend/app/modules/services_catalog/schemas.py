from pydantic import BaseModel, Field

class ServiceOut(BaseModel):
    code: str
    name: str
    description: str | None = None
    service_type: str
    active: bool = True
    display_order: int = 0

class ServiceCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None
    service_type: str = "standard"
    display_order: int = 0
