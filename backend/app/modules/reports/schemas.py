from datetime import date
from pydantic import BaseModel, Field

class ReportFilters(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    station_code: str | None = None
    partner_id: str | None = None
    customer_id: str | None = None
    status: str | None = None
    service_code: str | None = None
    city: str | None = None
    offer_code: str | None = None
    item_type: str | None = None
    category: str | None = None
    limit: int = Field(default=500, ge=1, le=5000)

aREPORT_TYPES = {
    "revenue", "orders", "customers", "partners", "stations", "garments",
    "hangers", "bags_boxes", "offers", "complaints", "customer_locations", "customer_history", "payments", "delivery", "notifications", "audit", "inventory_movements", "admin_actions",
}
