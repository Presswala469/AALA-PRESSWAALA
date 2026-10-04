from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from app.core.permissions import current_claims, require_role
from app.core.constants import UserRole
from fastapi import APIRouter, Depends, HTTPException
from app.modules.offers.schemas import OfferCreate, OfferApply
from app.modules.offers import service
router=APIRouter()
@router.post('',response_model=dict, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))])
def create(payload:OfferCreate): return service.create(payload.model_dump())
@router.get('',response_model=list)
def active(): return service.list_active()
@router.post('/apply',response_model=dict)
def apply(payload:OfferApply):
    try:return service.apply(payload.model_dump())
    except ValueError as e: raise HTTPException(400,str(e))

