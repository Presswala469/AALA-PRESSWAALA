from fastapi import APIRouter, HTTPException
from app.modules.hangers.schemas import HangerCreate,HangerStatus,HangerReturnCreate
from app.modules.hangers import service
router=APIRouter()
@router.post('',response_model=dict)
def create(payload:HangerCreate): return service.create(payload.model_dump())
@router.patch('/{hanger_id}',response_model=dict)
def update(hanger_id,payload:HangerStatus):
    try:return service.update(hanger_id,payload.model_dump())
    except ValueError as e: raise HTTPException(400,str(e))
@router.get('/{hanger_id}',response_model=dict)
def get(hanger_id): return service.get(hanger_id) or {}
@router.get('/customer/{customer_id}',response_model=list)
def customer(customer_id): return service.customer(customer_id)
@router.post('/returns',response_model=dict)
def request_return(payload:HangerReturnCreate): return service.request_return(payload.model_dump())
@router.get('/returns/{customer_id}',response_model=list)
def returns(customer_id): return service.returns(customer_id)

