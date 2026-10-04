from fastapi import APIRouter,HTTPException
from app.modules.orders.schemas import OrderCreate,OrderOut,OrderEventOut
from app.modules.orders.service import create,get,change_status,history
router=APIRouter()
@router.post('',response_model=OrderOut)
def create_order(payload:OrderCreate):
 try:return create(payload.model_dump())
 except ValueError as e:raise HTTPException(400,str(e))
@router.get('/{order_id}',response_model=OrderOut)
def read_order(order_id:str):
 row=get(order_id)
 if not row:raise HTTPException(404,'Order not found')
 return row
@router.post('/{order_id}/status',response_model=OrderOut)
def status(order_id:str,new_status:str,actor:str|None=None,reason:str|None=None):
 try:row=change_status(order_id,new_status,actor,reason)
 except ValueError as e:raise HTTPException(400,str(e))
 if not row:raise HTTPException(404,'Order not found')
 return row
@router.get('/{order_id}/events',response_model=list[OrderEventOut])
def order_events(order_id:str):
 if not get(order_id):raise HTTPException(404,'Order not found')
 return history(order_id)

