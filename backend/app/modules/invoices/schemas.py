from decimal import Decimal
from pydantic import BaseModel, Field
class InvoiceCreate(BaseModel): tax_amount: Decimal = Field(default=0, ge=0)
class InvoiceOut(BaseModel):
    invoice_id: str
    order_id: str
    invoice_number: str
    company_snapshot: dict
    subtotal: Decimal
    discount: Decimal
    tax_amount: Decimal
    total: Decimal
    currency: str
    issued_at: str
