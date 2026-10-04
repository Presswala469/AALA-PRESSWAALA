from fastapi import APIRouter, Depends
from app.core.permissions import require_role
from app.core.constants import UserRole
from app.modules.inventory.schemas import InventoryCreate, InventoryUpdate, InventoryAdjustment
from app.modules.inventory import service
router=APIRouter()
_admin=Depends(require_role(UserRole.SUPER_ADMIN,UserRole.ADMIN))
@router.post('',dependencies=[_admin])
def create(data: InventoryCreate): return service.create(data.model_dump())
@router.get('',dependencies=[_admin])
def list_items(status: str|None=None,item_type: str|None=None): return service.list_all(status,item_type)
@router.patch('/{inventory_id}',dependencies=[_admin])
def update(inventory_id:str,data:InventoryUpdate): return service.update(inventory_id,data.model_dump(exclude_none=True))
@router.post('/{inventory_id}/adjust',dependencies=[_admin])
def adjust(inventory_id:str,data:InventoryAdjustment): return service.adjust(inventory_id,data.model_dump())
@router.get('/{inventory_id}/history',dependencies=[_admin])
def history(inventory_id:str): return service.history(inventory_id)

