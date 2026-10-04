from fastapi import APIRouter,Depends,HTTPException
from app.core.constants import UserRole
from app.core.permissions import current_claims,require_role
from app.modules.zones.schemas import ZoneCreate,ZoneAssignmentCreate
from app.modules.zones import repository as repo
router=APIRouter()
_ADMIN=Depends(require_role(UserRole.SUPER_ADMIN,UserRole.ADMIN))
@router.get('',response_model=list,dependencies=[Depends(current_claims)])
def list_zones(): return repo.list_all()
@router.post('',response_model=dict,dependencies=[_ADMIN])
def create_zone(payload:ZoneCreate): return repo.create(payload.model_dump())
@router.post('/assign',response_model=dict,dependencies=[_ADMIN])
def assign_zone(payload:ZoneAssignmentCreate):
    try:return repo.assign(payload.model_dump())
    except ValueError as exc:raise HTTPException(400,str(exc))
