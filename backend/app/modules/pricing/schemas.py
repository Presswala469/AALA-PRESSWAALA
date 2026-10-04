from decimal import Decimal
from pydantic import BaseModel, Field
class PriceRuleCreate(BaseModel):
 service_code: str
 garment_code: str
 unit_price: Decimal = Field(ge=0)
 min_quantity: int = Field(default=1,ge=1)
 station_code: str | None = None
 express_surcharge: Decimal = Field(default=Decimal('0'),ge=0)
class PriceQuoteItem(BaseModel):
 garment_code: str
 quantity: int = Field(ge=1)
 unit_price: Decimal
 line_total: Decimal
class PriceQuoteRequest(BaseModel):
 service_code: str
 items: list[dict]
 station_code: str | None = None
class PriceQuote(BaseModel):
 service_code: str
 items: list[PriceQuoteItem]
 subtotal: Decimal
 surcharge: Decimal
 total: Decimal
 currency: str = 'INR'
