from pydantic import BaseModel, Field
class CreditCreate(BaseModel):
    customer_id: str
    amount: float = Field(gt=0)
    reason: str = Field(min_length=3)
    order_id: str | None = None
class RefundCreate(BaseModel):
    order_id: str
    amount: float = Field(gt=0)
    reason: str = Field(min_length=3)
    payment_id: str | None = None
class RefundUpdate(BaseModel):
    status: str = Field(pattern='^(APPROVED|REJECTED|PROCESSED)$')
    remarks: str | None = None
