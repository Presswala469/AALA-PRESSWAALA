from fastapi import APIRouter, Depends, HTTPException

from app.core.permissions import current_claims
from app.modules.payments.schemas import PaymentCreate, PaymentVerify
from app.modules.payments import service

router = APIRouter()


def err(exc: ValueError) -> None:
    raise HTTPException(400, str(exc))


_AUTH = Depends(current_claims)


@router.post("/orders/{order_id}", response_model=dict, dependencies=[_AUTH])
def create(order_id: str, payload: PaymentCreate):
    try:
        return service.create(order_id, payload.method)
    except ValueError as exc:
        err(exc)


@router.post("/{payment_id}/verify", response_model=dict, dependencies=[_AUTH])
def verify(payment_id: str, payload: PaymentVerify):
    try:
        return service.verify(payment_id, payload.model_dump())
    except ValueError as exc:
        err(exc)


@router.get("/{payment_id}", response_model=dict, dependencies=[_AUTH])
def get(payment_id: str):
    return service.get(payment_id) or {}


@router.get("/orders/{order_id}", response_model=list, dependencies=[_AUTH])
def list_order(order_id: str):
    return service.list_for_order(order_id)
