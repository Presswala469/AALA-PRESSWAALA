from decimal import Decimal
from pydantic import BaseModel, Field
class PaymentCreate(BaseModel):
    method: str = Field(pattern='^(UPI|CARD|COD)$')
class PaymentVerify(BaseModel):
    provider_order_id: str
    provider_payment_id: str
    signature: str | None = None
class PaymentOut(BaseModel):
    payment_id: str
    order_id: str
    method: str
    amount: Decimal
    currency: str
    status: str
    provider: str
    provider_order_id: str | None = None
    provider_payment_id: str | None = None
