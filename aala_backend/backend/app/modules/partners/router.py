from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from app.core.permissions import current_claims, require_role
from app.core.constants import UserRole
from fastapi import APIRouter, Depends, HTTPException
from app.modules.partners.schemas import *
from app.modules.partners import service
router=APIRouter()
@router.post('',response_model=PartnerOut, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))])
def create(payload:PartnerCreate): return service.create(payload.model_dump())
@router.get('',response_model=list[PartnerOut])
def list_(station_code:str|None=None): return service.list_all(station_code)
@router.post('/{partner_id}/assign',response_model=dict, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STATION_MANAGER))])
def assign(partner_id:str,payload:PartnerAssign):
    try:return service.assign(partner_id,payload.station_code)
    except ValueError as e: raise HTTPException(404,str(e))
@router.get('/{partner_id}/assignment',response_model=dict)
def assignment(partner_id:str): return service.assignment(partner_id) or {}
@router.post('/{partner_id}/orders/{order_id}/pickup-start',response_model=dict)
def pickup_start(partner_id:str,order_id:str):
    try:
        row=service.mark_pickup_started(order_id,partner_id)
        if not row: raise HTTPException(404,'Order not found')
        return row
    except ValueError as e: raise HTTPException(400,str(e))
@router.post('/{partner_id}/orders/{order_id}/arrival',response_model=dict)
def customer_arrival(partner_id:str,order_id:str,payload:PickupArrival): return service.arrival(order_id,partner_id,payload.model_dump())
@router.post('/{partner_id}/orders/{order_id}/verify-garments',response_model=dict)
def verify_garments(partner_id:str,order_id:str,payload:GarmentVerification): return service.verify(order_id,partner_id,payload.model_dump())
@router.post('/{partner_id}/orders/{order_id}/damage',response_model=dict)
def damage(partner_id:str,order_id:str,payload:DamageEvidence): return service.damage(order_id,partner_id,payload.model_dump())
@router.post('/{partner_id}/orders/{order_id}/bag',response_model=dict)
def bag(partner_id:str,order_id:str,payload:BagAssignment): return service.bag(order_id,partner_id,payload.model_dump())
@router.post('/{partner_id}/orders/{order_id}/pickup-complete',response_model=dict)
def pickup_complete(partner_id:str,order_id:str,payload:PickupComplete):
    row=service.complete(order_id,partner_id,payload.model_dump())
    try:
        service.mark_station_handover(order_id,partner_id,payload.notes)
    except ValueError as e: raise HTTPException(400,str(e))
    return row

