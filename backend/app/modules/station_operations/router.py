from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.constants import UserRole
from app.core.permissions import (
    current_claims,
    enforce_partner_station,
    enforce_station_access,
    enforce_station_order_access,
    require_role,
)
from app.modules.station_operations.schemas import StationArrival, StationReceive, StationStatusUpdate, StationEvidence
from app.modules.station_operations import service

router = APIRouter()


def _error(exc: ValueError) -> None:
    raise HTTPException(status_code=400, detail=str(exc))


_STATION_ROLES = (UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STATION_MANAGER)
_STATION_READ = Depends(require_role(*_STATION_ROLES))
_STATION_WRITE = Depends(require_role(*_STATION_ROLES))
_PARTNER_ARRIVAL = Depends(require_role(*(_STATION_ROLES + (UserRole.PARTNER,))))


@router.get("/stations/{station_code}/incoming", response_model=list, dependencies=[_STATION_READ])
def incoming(station_code: str, claims=Depends(current_claims)):
    enforce_station_access(station_code, claims)
    return service.incoming(station_code)


@router.post("/orders/{order_id}/arrival", response_model=dict, dependencies=[_PARTNER_ARRIVAL])
def arrival(order_id: str, payload: StationArrival, station_code: str = Query(...), partner_id: str = Query(...), claims=Depends(current_claims)):
    try:
        enforce_partner_station(partner_id, station_code, claims)
        return service.arrival(order_id, station_code, partner_id, payload.model_dump())
    except ValueError as exc:
        _error(exc)


@router.post("/orders/{order_id}/receive", response_model=dict, dependencies=[_STATION_WRITE])
def receive(order_id: str, payload: StationReceive, station_code: str = Query(...), partner_id: str = Query(...), claims=Depends(current_claims)):
    try:
        enforce_station_access(station_code, claims)
        return service.receive(order_id, station_code, partner_id, payload.model_dump())
    except ValueError as exc:
        _error(exc)


@router.post("/orders/{order_id}/status", response_model=dict, dependencies=[_STATION_WRITE])
def status(order_id: str, payload: StationStatusUpdate, station_code: str = Query(...), claims=Depends(current_claims)):
    try:
        enforce_station_access(station_code, claims)
        return service.status(order_id, station_code, payload.model_dump())
    except ValueError as exc:
        _error(exc)


@router.post("/orders/{order_id}/evidence", response_model=dict, dependencies=[_STATION_WRITE])
def evidence(order_id: str, payload: StationEvidence, station_code: str = Query(...), actor: str = Query(...), claims=Depends(current_claims)):
    try:
        enforce_station_access(station_code, claims)
        # Preserve the public parameter for compatibility, but do not trust it for authorization.
        actor = f"{claims.get('role')}:{claims.get('sub')}"
        return service.evidence(order_id, station_code, actor, payload.model_dump())
    except ValueError as exc:
        _error(exc)


@router.get("/orders/{order_id}/receipt", response_model=dict, dependencies=[_STATION_READ])
def receipt(order_id: str, claims=Depends(current_claims)):
    enforce_station_order_access(order_id, claims)
    return service.receipt(order_id) or {}


@router.get("/orders/{order_id}/history", response_model=list, dependencies=[_STATION_READ])
def history(order_id: str, claims=Depends(current_claims)):
    enforce_station_order_access(order_id, claims)
    return service.history(order_id)
