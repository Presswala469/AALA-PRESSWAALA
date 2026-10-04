from decimal import Decimal
from pydantic import BaseModel, Field
class OrderItemCreate(BaseModel):
 garment_code: str
 quantity: int = Field(ge=1)
class OrderCreate(BaseModel):
 customer_id: str
 address_id: str
 service_code: str
 pickup_slot_id: str
 items: list[OrderItemCreate] = Field(min_length=1)
 offer_code: str | None = None
 payment_method: str = 'UPI'
 station_code: str | None = None
 notes: str | None = None
class OrderItemOut(BaseModel):
 garment_code: str
 quantity: int
 unit_price: Decimal
 line_total: Decimal
class OrderOut(BaseModel):
 order_id: str
 customer_id: str
 address_id: str
 service_code: str
 pickup_slot_id: str
 status: str
 currency: str
 subtotal: Decimal
 discount: Decimal
 total: Decimal
 payment_method: str
 items: list[OrderItemOut]
 created_at: str
 customer_snapshot: dict | None = None
 address_snapshot: dict | None = None
 booking_snapshot: dict | None = None
 tat_started_at: str | None = None
 tat_due_at: str | None = None
 tat_completed_at: str | None = None
class OrderEventOut(BaseModel):
 event_type: str
 from_status: str | None
 to_status: str | None
 actor: str | None
 created_at: str
 customer_snapshot: dict | None = None
 address_snapshot: dict | None = None
 booking_snapshot: dict | None = None
 tat_started_at: str | None = None
 tat_due_at: str | None = None
 tat_completed_at: str | None = None
