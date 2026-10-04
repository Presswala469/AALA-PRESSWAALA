from fastapi import APIRouter, Depends, HTTPException

from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from app.modules.hangers.schemas import HangerCreate, HangerStatus, HangerReturnCreate
from app.modules.hangers import service

router = APIRouter()

_AUTH = Depends(current_claims)
_OPERATIONS = Depends(
    require_role(
        UserRole.SUPER_ADMIN,
        UserRole.ADMIN,
        UserRole.STATION_MANAGER,
        UserRole.PARTNER,
    )
)


@router.post("", response_model=dict, dependencies=[_AUTH])
def create(payload: HangerCreate):
    return service.create(payload.model_dump())


@router.patch("/{hanger_id}", response_model=dict, dependencies=[_OPERATIONS])
def update(hanger_id: str, payload: HangerStatus):
    try:
        return service.update(hanger_id, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.get("/{hanger_id}", response_model=dict, dependencies=[_AUTH])
def get(hanger_id: str):
    return service.get(hanger_id) or {}


@router.get("/customer/{customer_id}", response_model=list, dependencies=[_AUTH])
def customer(customer_id: str):
    return service.customer(customer_id)


@router.post("/returns", response_model=dict, dependencies=[_AUTH])
def request_return(payload: HangerReturnCreate):
    return service.request_return(payload.model_dump())


@router.get("/returns/{customer_id}", response_model=list, dependencies=[_AUTH])
def returns(customer_id: str):
    return service.returns(customer_id)
