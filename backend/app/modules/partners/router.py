from fastapi import APIRouter, Depends, HTTPException

from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role, enforce_partner_identity
from app.modules.partners.schemas import *
from app.modules.partners import service

router = APIRouter()

_ADMIN = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))
_OPERATIONS = Depends(
    require_role(
        UserRole.SUPER_ADMIN,
        UserRole.ADMIN,
        UserRole.STATION_MANAGER,
        UserRole.PARTNER,
    )
)


@router.post("", response_model=PartnerOut, dependencies=[_ADMIN])
def create(payload: PartnerCreate):
    return service.create(payload.model_dump())


@router.get("", response_model=list[PartnerOut], dependencies=[Depends(current_claims)])
def list_(station_code: str | None = None, claims=Depends(current_claims)):
    if claims.get("role") == UserRole.PARTNER.value:
        return service.list_for_partner_claims(claims)
    return service.list_all(station_code)


@router.post(
    "/{partner_id}/assign",
    response_model=dict,
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STATION_MANAGER))],
)
def assign(partner_id: str, payload: PartnerAssign):
    try:
        return service.assign(partner_id, payload.station_code)
    except ValueError as exc:
        raise HTTPException(404, str(exc))


@router.get("/{partner_id}/assignment", response_model=dict, dependencies=[_OPERATIONS])
def assignment(partner_id: str, claims=Depends(current_claims)):
    partner_id = enforce_partner_identity(partner_id, claims)
    return service.assignment(partner_id) or {}


@router.post(
    "/{partner_id}/orders/{order_id}/pickup-start",
    response_model=dict,
    dependencies=[_OPERATIONS],
)
def pickup_start(partner_id: str, order_id: str, claims=Depends(current_claims)):
    partner_id = enforce_partner_identity(partner_id, claims)
    try:
        row = service.mark_pickup_started(order_id, partner_id)
        if not row:
            raise HTTPException(404, "Order not found")
        return row
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.post(
    "/{partner_id}/orders/{order_id}/arrival",
    response_model=dict,
    dependencies=[_OPERATIONS],
)
def customer_arrival(partner_id: str, order_id: str, payload: PickupArrival, claims=Depends(current_claims)):
    partner_id = enforce_partner_identity(partner_id, claims)
    return service.arrival(order_id, partner_id, payload.model_dump())


@router.post(
    "/{partner_id}/orders/{order_id}/verify-garments",
    response_model=dict,
    dependencies=[_OPERATIONS],
)
def verify_garments(partner_id: str, order_id: str, payload: GarmentVerification, claims=Depends(current_claims)):
    partner_id = enforce_partner_identity(partner_id, claims)
    return service.verify(order_id, partner_id, payload.model_dump())


@router.post(
    "/{partner_id}/orders/{order_id}/damage",
    response_model=dict,
    dependencies=[_OPERATIONS],
)
def damage(partner_id: str, order_id: str, payload: DamageEvidence, claims=Depends(current_claims)):
    partner_id = enforce_partner_identity(partner_id, claims)
    return service.damage(order_id, partner_id, payload.model_dump())


@router.post(
    "/{partner_id}/orders/{order_id}/bag",
    response_model=dict,
    dependencies=[_OPERATIONS],
)
def bag(partner_id: str, order_id: str, payload: BagAssignment, claims=Depends(current_claims)):
    partner_id = enforce_partner_identity(partner_id, claims)
    return service.bag(order_id, partner_id, payload.model_dump())


@router.post(
    "/{partner_id}/orders/{order_id}/pickup-complete",
    response_model=dict,
    dependencies=[_OPERATIONS],
)
def pickup_complete(partner_id: str, order_id: str, payload: PickupComplete, claims=Depends(current_claims)):
    partner_id = enforce_partner_identity(partner_id, claims)
    row = service.complete(order_id, partner_id, payload.model_dump())
    try:
        service.mark_station_handover(order_id, partner_id, payload.notes)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return row
