from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from fastapi import APIRouter, Depends,HTTPException
from app.modules.pickup.schemas import PickupSlotCreate,PickupSlotOut,PickupJobAssign,PickupJobOut
from app.modules.pickup.service import slots,save,assign,job
router=APIRouter()
@router.get('/slots',response_model=list[PickupSlotOut])
def pickup_slots(station_code:str|None=None): return slots(station_code)
@router.post('/slots',response_model=PickupSlotOut, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STATION_MANAGER))])
def create_slot(payload:PickupSlotCreate): return save(payload.model_dump())
@router.post('/orders/{order_id}/assign',response_model=PickupJobOut, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STATION_MANAGER))])
def assign_pickup(order_id:str,payload:PickupJobAssign): return assign(order_id,payload.partner_id)
@router.get('/orders/{order_id}/job',response_model=PickupJobOut, dependencies=[Depends(current_claims)])
def pickup_job(order_id:str):
    row=job(order_id)
    if not row: raise HTTPException(404,'Pickup job not found')
    return row

