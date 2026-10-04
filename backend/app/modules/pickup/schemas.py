from pydantic import BaseModel,Field
class PickupSlotCreate(BaseModel):
 slot_id: str = Field(min_length=2,max_length=50); label: str; start_time: str; end_time: str; station_code: str|None=None; max_orders:int=Field(default=20,ge=1); active:bool=True
class PickupSlotOut(PickupSlotCreate): pass
class PickupJobAssign(BaseModel): partner_id:str
class PickupJobOut(BaseModel): order_id:str; partner_id:str; assigned_at:str
