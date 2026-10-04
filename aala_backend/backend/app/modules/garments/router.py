from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from app.core.permissions import current_claims, require_role
from app.core.constants import UserRole
from fastapi import APIRouter, Depends,HTTPException
from app.modules.garments.schemas import GarmentCategoryCreate,GarmentCategoryOut
from app.modules.garments.service import list_active,get,save
router=APIRouter()
@router.get("",response_model=list[GarmentCategoryOut])
def categories(): return list_active()
@router.get("/{code}",response_model=GarmentCategoryOut)
def category(code:str):
 row=get(code)
 if not row: raise HTTPException(404,"Garment category not found")
 return row
@router.post("",response_model=GarmentCategoryOut, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))])
def create_category(payload:GarmentCategoryCreate): return save(payload.model_dump())

