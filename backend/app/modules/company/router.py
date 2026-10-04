from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from fastapi import APIRouter, Depends

from app.core.constants import UserRole
from app.core.permissions import require_role
from app.modules.company.schemas import CompanyPublic, CompanyUpdate
from app.modules.company.service import public_config, save_company

router = APIRouter()

@router.get("/public", response_model=CompanyPublic)
def get_public_company():
    return public_config()

@router.get("/settings", dependencies=[Depends(current_claims)])
def get_company_settings(claims=Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))):
    return public_config()

@router.put("/settings", dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))])
def put_company_settings(payload: CompanyUpdate, claims=Depends(require_role(UserRole.SUPER_ADMIN))):
    return save_company(payload.model_dump(exclude_none=True), claims["sub"])

