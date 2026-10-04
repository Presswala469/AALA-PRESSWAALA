from fastapi import APIRouter, Depends

from app.core.permissions import current_claims, enforce_customer_identity
from app.modules.addresses.schemas import AddressCreate
from app.modules.addresses.service import create, list_current_and_history

router = APIRouter()
_AUTH = Depends(current_claims)


@router.post("", dependencies=[_AUTH])
def create_address(payload: AddressCreate, claims=Depends(current_claims)):
    enforce_customer_identity(payload.customer_id, claims)
    return create(payload.model_dump())


@router.get("/customer/{customer_id}", dependencies=[_AUTH])
def list_addresses(customer_id: str, claims=Depends(current_claims)):
    enforce_customer_identity(customer_id, claims)
    return list_current_and_history(customer_id)
