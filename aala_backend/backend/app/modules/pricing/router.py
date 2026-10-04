from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from app.core.permissions import current_claims, require_role
from app.core.constants import UserRole
from fastapi import APIRouter, Depends,HTTPException
from app.modules.pricing.schemas import PriceRuleCreate,PriceQuoteRequest,PriceQuote
from app.modules.pricing.service import quote,save_price
router=APIRouter()
@router.post('/quote',response_model=PriceQuote)
def create_quote(payload:PriceQuoteRequest):
 try:return quote(payload.service_code,payload.items,payload.station_code)
 except ValueError as e: raise HTTPException(400,str(e))
@router.post('/rules', dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))])
def create_rule(payload:PriceRuleCreate): return save_price(payload.model_dump())

