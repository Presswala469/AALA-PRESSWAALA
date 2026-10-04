from fastapi import APIRouter, Depends
from app.core.permissions import require_role
from app.core.constants import UserRole
from app.modules.audit import service
router=APIRouter()
_admin=Depends(require_role(UserRole.SUPER_ADMIN,UserRole.ADMIN))
@router.get('',dependencies=[_admin])
def logs(entity_type:str|None=None,limit:int=100): return service.list_all(entity_type,min(limit,500))

