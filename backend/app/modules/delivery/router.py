from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.constants import UserRole
from app.core.permissions import require_role, current_claims, enforce_partner_identity
from app.modules.delivery.schemas import DeliveryAssign, DeliveryStart, DeliveryConfirm, DeliveryException
from app.modules.delivery import service

router = APIRouter()


def err(exc: ValueError) -> None:
    raise HTTPException(400, str(exc))


_ASSIGN = Depends(
    require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STATION_MANAGER)
)
_PARTNER_OPS = Depends(
    require_role(
        UserRole.SUPER_ADMIN,
        UserRole.ADMIN,
        UserRole.STATION_MANAGER,
        UserRole.PARTNER,
    )
)


@router.post("/orders/{order_id}/assign", response_model=dict, dependencies=[_ASSIGN])
def assign(order_id: str, payload: DeliveryAssign):
    try:
        return service.assign(order_id, payload.partner_id)
    except ValueError as exc:
        err(exc)


@router.post("/orders/{order_id}/start", response_model=dict, dependencies=[_PARTNER_OPS])
def start(order_id: str, payload: DeliveryStart, claims=Depends(current_claims)):
    partner_id = enforce_partner_identity(payload.partner_id, claims)
    try:
        return service.start(order_id, partner_id)
    except ValueError as exc:
        err(exc)


@router.post("/orders/{order_id}/confirm", response_model=dict, dependencies=[_PARTNER_OPS])
def confirm(order_id: str, payload: DeliveryConfirm, partner_id: str = Query(...), claims=Depends(current_claims)):
    partner_id = enforce_partner_identity(partner_id, claims)
    try:
        return service.confirm(order_id, partner_id, payload.model_dump())
    except ValueError as exc:
        err(exc)


@router.post("/orders/{order_id}/exception", response_model=dict, dependencies=[_PARTNER_OPS])
def exception(order_id: str, payload: DeliveryException, partner_id: str = Query(...), claims=Depends(current_claims)):
    partner_id = enforce_partner_identity(partner_id, claims)
    try:
        return service.exception(order_id, partner_id, payload.model_dump())
    except ValueError as exc:
        err(exc)


@router.get("/orders/{order_id}", response_model=dict, dependencies=[_PARTNER_OPS])
def get_job(order_id: str, claims=Depends(current_claims)):
    try:
        service.authorize_view(order_id, claims)
    except ValueError as exc:
        err(exc)
    return service.get_job(order_id) or {}


@router.get("/orders/{order_id}/code", response_model=dict, dependencies=[_PARTNER_OPS])
def get_code(order_id: str, claims=Depends(current_claims)):
    try:
        service.authorize_view(order_id, claims)
    except ValueError as exc:
        err(exc)
    return service.get_code(order_id) or {}
