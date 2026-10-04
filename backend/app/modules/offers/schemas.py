from decimal import Decimal
from pydantic import BaseModel, Field
class OfferCreate(BaseModel):
    code: str = Field(min_length=2,max_length=40)
    name: str
    discount_type: str = Field(pattern='^(PERCENT|FLAT)$')
    discount_value: Decimal = Field(gt=0)
    start_at: str | None = None; end_at: str | None = None
    days: list[int] = Field(default_factory=list)
    customer_type: str | None = None
    min_order: Decimal = Field(default=0,ge=0); max_discount: Decimal | None = Field(default=None,ge=0)
    priority: int = 0; enabled: bool = True
    city: str | None=None; station_code: str | None=None; area: str | None=None; building: str | None=None
class OfferApply(BaseModel):
    code: str; subtotal: Decimal = Field(ge=0); customer_type: str | None=None; city: str | None=None; station_code: str | None=None; area: str | None=None; building: str | None=None
