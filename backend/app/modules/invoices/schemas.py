from decimal import Decimal
from pydantic import BaseModel, Field


class InvoiceCreate(BaseModel):
    tax_rate: Decimal = Field(default=Decimal('0'), ge=0, le=100)
    tax_type: str = Field(default='GST', pattern='^(GST|NONE)$')
    tax_mode: str = Field(default='INTRA', pattern='^(INTRA|INTER|NONE)$')
    payment_reference: str | None = Field(default=None, max_length=160)


class InvoiceOut(BaseModel):
    invoice_id: str
    order_id: str
    invoice_number: str
    company_snapshot: dict
    customer_snapshot: dict
    order_snapshot: dict
    subtotal: Decimal
    discount: Decimal
    tax_amount: Decimal
    tax_rate: Decimal
    cgst_amount: Decimal
    sgst_amount: Decimal
    igst_amount: Decimal
    tax_type: str
    total: Decimal
    currency: str
    payment_reference: str | None = None
    status: str
    issued_at: str
    updated_at: str
    items: list[dict] = []
