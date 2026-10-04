from fastapi import APIRouter, Depends
from app.core.constants import UserRole
from app.core.permissions import require_role
from .schemas import CreditCreate, RefundCreate, RefundUpdate
from . import repository as repo
router=APIRouter()
_admin=Depends(require_role(UserRole.SUPER_ADMIN,UserRole.ADMIN))
@router.post('/credits',dependencies=[_admin])
def credit(data:CreditCreate,claims=Depends(require_role(UserRole.SUPER_ADMIN,UserRole.ADMIN))): return repo.create_credit(data.model_dump(),claims['sub'])
@router.get('/credits/{customer_id}',dependencies=[_admin])
def credits(customer_id:str): return repo.list_credits(customer_id)
@router.post('/refunds',dependencies=[_admin])
def refund(data:RefundCreate,claims=Depends(require_role(UserRole.SUPER_ADMIN,UserRole.ADMIN))): return repo.create_refund(data.model_dump(),claims['sub'])
@router.patch('/refunds/{refund_id}',dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))])
def refund_update(refund_id:str,data:RefundUpdate,claims=Depends(require_role(UserRole.SUPER_ADMIN))): return repo.update_refund(refund_id,data.model_dump(exclude_none=True),claims['sub'])
@router.get('/refunds/{refund_id}',dependencies=[_admin])
def refund_get(refund_id:str): return repo.get_refund(refund_id)
