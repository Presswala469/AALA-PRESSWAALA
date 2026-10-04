from fastapi import APIRouter, Depends, HTTPException

from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role, enforce_customer_identity, enforce_station_order_access
from app.modules.orders.schemas import OrderCreate, OrderOut, OrderEventOut
from app.modules.orders.service import create, get, change_status, history, reorder
from app.modules.orders.tat import set_rule, get_rule
from app.modules.orders.tat_schemas import TATRuleCreate, TATRuleOut
from app.core.config import settings

router = APIRouter()

_ORDER_ACTOR = Depends(
    require_role(
        UserRole.SUPER_ADMIN,
        UserRole.ADMIN,
        UserRole.STATION_MANAGER,
        UserRole.PARTNER,
    )
)


@router.post("", response_model=OrderOut, dependencies=[Depends(current_claims)])
def create_order(payload: OrderCreate, claims=Depends(current_claims)):
    try:
        if settings.database_url and claims.get("role") == UserRole.CUSTOMER.value:
            enforce_customer_identity(payload.customer_id, claims)
        return create(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.get("/{order_id}", response_model=OrderOut, dependencies=[Depends(current_claims)])
def read_order(order_id: str, claims=Depends(current_claims)):
    row = get(order_id)
    if not row:
        raise HTTPException(404, "Order not found")
    if settings.database_url:
        if claims.get("role") == UserRole.CUSTOMER.value:
            enforce_customer_identity(row["customer_id"], claims)
        elif claims.get("role") == UserRole.STATION_MANAGER.value:
            enforce_station_order_access(order_id, claims)
    return row


@router.post("/{order_id}/status", response_model=OrderOut, dependencies=[_ORDER_ACTOR])
def status(order_id: str, new_status: str, actor: str | None = None, reason: str | None = None):
    try:
        row = change_status(order_id, new_status, actor, reason)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    if not row:
        raise HTTPException(404, "Order not found")
    return row


@router.get("/{order_id}/events", response_model=list[OrderEventOut], dependencies=[Depends(current_claims)])
def order_events(order_id: str, claims=Depends(current_claims)):
    row=get(order_id)
    if not row:
        raise HTTPException(404, "Order not found")
    if settings.database_url:
        if claims.get("role") == UserRole.CUSTOMER.value:
            enforce_customer_identity(row["customer_id"], claims)
        elif claims.get("role") == UserRole.STATION_MANAGER.value:
            enforce_station_order_access(order_id, claims)
    return history(order_id)


@router.post('/{order_id}/reorder', response_model=OrderOut, dependencies=[Depends(current_claims)])
def reorder_order(order_id: str, claims=Depends(current_claims)):
    try:
        order=get(order_id)
        if not order: raise HTTPException(404,'Order not found')
        if settings.database_url and claims.get('role') == UserRole.CUSTOMER.value:
            enforce_customer_identity(order['customer_id'],claims)
        customer_id=order['customer_id']
        return reorder(order_id,customer_id)
    except ValueError as exc:
        raise HTTPException(400,str(exc))

@router.post('/tat/rules', response_model=TATRuleOut, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN,UserRole.ADMIN))])
def create_tat_rule(payload:TATRuleCreate):
    return set_rule(payload.service_code,payload.target_minutes,payload.urgent_threshold_minutes)

@router.get('/tat/rules/{service_code}', response_model=TATRuleOut, dependencies=[Depends(current_claims)])
def read_tat_rule(service_code:str):
    row=get_rule(service_code)
    if not row: raise HTTPException(404,'TAT rule not configured')
    return row
