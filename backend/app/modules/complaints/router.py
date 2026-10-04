from fastapi import APIRouter, Depends, HTTPException

from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from app.modules.complaints.schemas import ComplaintCreate, ComplaintStatusUpdate
from app.modules.complaints import service

router = APIRouter()

_AUTH = Depends(current_claims)
_ADMIN = Depends(
    require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STATION_MANAGER)
)


@router.post("", response_model=dict, dependencies=[_AUTH])
def create(payload: ComplaintCreate):
    try:
        return service.create(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.patch("/{complaint_id}", response_model=dict, dependencies=[_ADMIN])
def update(complaint_id: str, payload: ComplaintStatusUpdate):
    try:
        return service.update(complaint_id, payload.model_dump())
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.get("/{complaint_id}", response_model=dict, dependencies=[_AUTH])
def get(complaint_id: str):
    return service.get(complaint_id) or {}


@router.get("/{complaint_id}/events", response_model=list, dependencies=[_AUTH])
def events(complaint_id: str):
    return service.events(complaint_id)
