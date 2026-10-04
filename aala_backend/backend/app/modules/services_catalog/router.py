from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from app.core.permissions import current_claims, require_role
from app.core.constants import UserRole
from fastapi import APIRouter, Depends, HTTPException
from app.modules.services_catalog.schemas import ServiceCreate, ServiceOut
from app.modules.services_catalog.service import list_active,get,save
router=APIRouter()
@router.get("",response_model=list[ServiceOut])
def services(): return list_active()
@router.get("/{code}",response_model=ServiceOut)
def service(code:str):
    row=get(code)
    if not row: raise HTTPException(404,"Service not found")
    return row
@router.post("",response_model=ServiceOut, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))])
def create_service(payload:ServiceCreate): return save(payload.model_dump())

