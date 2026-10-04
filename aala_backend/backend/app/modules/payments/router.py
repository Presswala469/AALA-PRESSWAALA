from fastapi import APIRouter, HTTPException
from app.modules.payments.schemas import PaymentCreate, PaymentVerify
from app.modules.payments import service
router=APIRouter()
def err(e): raise HTTPException(400,str(e))
@router.post('/orders/{order_id}',response_model=dict)
def create(order_id,payload:PaymentCreate):
    try:return service.create(order_id,payload.method)
    except ValueError as e: err(e)
@router.post('/{payment_id}/verify',response_model=dict)
def verify(payment_id,payload:PaymentVerify):
    try:return service.verify(payment_id,payload.model_dump())
    except ValueError as e: err(e)
@router.get('/{payment_id}',response_model=dict)
def get(payment_id): return service.get(payment_id) or {}
@router.get('/orders/{order_id}',response_model=list)
def list_order(order_id): return service.list_for_order(order_id)

