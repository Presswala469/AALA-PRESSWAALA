from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from app.core.permissions import current_claims, require_role
from app.core.constants import UserRole
from fastapi import APIRouter, Depends, HTTPException, Query
from app.modules.delivery.schemas import DeliveryAssign, DeliveryStart, DeliveryConfirm, DeliveryException
from app.modules.delivery import service
router=APIRouter()
def err(e): raise HTTPException(400,str(e))
@router.post('/orders/{order_id}/assign',response_model=dict, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STATION_MANAGER))])
def assign(order_id,payload:DeliveryAssign):
    try:return service.assign(order_id,payload.partner_id)
    except ValueError as e: err(e)
@router.post('/orders/{order_id}/start',response_model=dict)
def start(order_id,payload:DeliveryStart):
    try:return service.start(order_id,payload.partner_id)
    except ValueError as e: err(e)
@router.post('/orders/{order_id}/confirm',response_model=dict)
def confirm(order_id,payload:DeliveryConfirm,partner_id:str=Query(...)):
    try:return service.confirm(order_id,partner_id,payload.model_dump())
    except ValueError as e: err(e)
@router.post('/orders/{order_id}/exception',response_model=dict)
def exception(order_id,payload:DeliveryException,partner_id:str=Query(...)):
    try:return service.exception(order_id,partner_id,payload.model_dump())
    except ValueError as e: err(e)
@router.get('/orders/{order_id}',response_model=dict)
def get_job(order_id): return service.get_job(order_id) or {}
@router.get('/orders/{order_id}/code',response_model=dict)
def get_code(order_id): return service.get_code(order_id) or {}

