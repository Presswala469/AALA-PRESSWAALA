from pydantic import BaseModel, Field

class CustomerCreate(BaseModel):
    mobile_number: str = Field(min_length=10, max_length=20)
    full_name: str = Field(min_length=1, max_length=150)
    email: str | None = None

class CustomerOut(BaseModel):
    customer_id: str
    global_customer_number: int
    mobile_number: str
    full_name: str
    email: str | None = None
    is_active: bool
