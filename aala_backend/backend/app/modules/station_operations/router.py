from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from app.core.permissions import current_claims, require_role
from app.core.constants import UserRole
from fastapi import APIRouter, Depends, HTTPException, Query
from app.modules.station_operations.schemas import StationArrival, StationReceive, StationStatusUpdate, StationEvidence
from app.modules.station_operations import service

router=APIRouter()

def _error(e): raise HTTPException(400,str(e))

@router.get('/stations/{station_code}/incoming',response_model=list)
def incoming(station_code:str): return service.incoming(station_code)

@router.post('/orders/{order_id}/arrival',response_model=dict, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STATION_MANAGER, UserRole.PARTNER))])
def arrival(order_id:str,payload:StationArrival,station_code:str=Query(...),partner_id:str=Query(...)):
    try:return service.arrival(order_id,station_code,partner_id,payload.model_dump())
    except ValueError as e:_error(e)

@router.post('/orders/{order_id}/receive',response_model=dict)
def receive(order_id:str,payload:StationReceive,station_code:str=Query(...),partner_id:str=Query(...)):
    try:return service.receive(order_id,station_code,partner_id,payload.model_dump())
    except ValueError as e:_error(e)

@router.post('/orders/{order_id}/status',response_model=dict)
def status(order_id:str,payload:StationStatusUpdate,station_code:str=Query(...)):
    try:return service.status(order_id,station_code,payload.model_dump())
    except ValueError as e:_error(e)

@router.post('/orders/{order_id}/evidence',response_model=dict)
def evidence(order_id:str,payload:StationEvidence,station_code:str=Query(...),actor:str=Query(...)):
    try:return service.evidence(order_id,station_code,actor,payload.model_dump())
    except ValueError as e:_error(e)

@router.get('/orders/{order_id}/receipt',response_model=dict)
def receipt(order_id:str): return service.receipt(order_id) or {}

@router.get('/orders/{order_id}/history',response_model=list)
def history(order_id:str): return service.history(order_id)

