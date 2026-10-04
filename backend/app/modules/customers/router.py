from fastapi import APIRouter, Depends, HTTPException

from app.core.permissions import current_claims, enforce_customer_identity
from app.modules.customers.schemas import CustomerCreate, CustomerOut
from app.modules.customers.service import create, get

router = APIRouter()
_AUTH = Depends(current_claims)


@router.post("", response_model=CustomerOut, dependencies=[_AUTH])
def create_customer(payload: CustomerCreate):
    return create(payload.model_dump())


@router.get("/{customer_id}", response_model=CustomerOut, dependencies=[_AUTH])
def read_customer(customer_id: str, claims=Depends(current_claims)):
    enforce_customer_identity(customer_id, claims)
    row = get(customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row
