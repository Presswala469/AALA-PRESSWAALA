from fastapi import APIRouter, Depends, HTTPException
from app.core.permissions import current_claims, enforce_customer_identity
from app.modules.ratings.schemas import RatingCreate, RatingOut
from app.modules.ratings import service
from app.modules.orders.service import get as get_order

router=APIRouter()

@router.post('/orders/{order_id}', response_model=RatingOut, dependencies=[Depends(current_claims)])
def create_rating(order_id: str, payload: RatingCreate, claims=Depends(current_claims)):
    try:
        order=get_order(order_id)
        if not order: raise HTTPException(404,'Order not found')
        enforce_customer_identity(order['customer_id'], claims)
        if payload.customer_id != order['customer_id']:
            raise HTTPException(403,'Customer access denied')
        return service.create(order_id,payload.model_dump())
    except ValueError as exc:
        raise HTTPException(400,str(exc))

@router.get('/orders/{order_id}', response_model=RatingOut, dependencies=[Depends(current_claims)])
def get_rating(order_id: str, claims=Depends(current_claims)):
    order=get_order(order_id)
    if not order: raise HTTPException(404,'Order not found')
    role=claims.get('role')
    if role=='customer': enforce_customer_identity(order['customer_id'], claims)
    row=service.get(order_id)
    if not row: raise HTTPException(404,'Rating not found')
    return row
