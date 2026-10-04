from pydantic import BaseModel, Field
class HangerCreate(BaseModel): hanger_id: str | None=None; customer_id: str; order_id: str | None=None; quantity: int = Field(default=1,ge=1)
class HangerStatus(BaseModel): status: str = Field(pattern='^(ISSUED|RETURNED|PENDING)$'); remarks: str | None=None
class HangerReturnCreate(BaseModel): customer_id: str; address_id: str; quantity: int = Field(ge=1); preferred_slot_id: str | None=None
