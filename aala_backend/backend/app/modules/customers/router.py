from fastapi import APIRouter, HTTPException
from app.modules.customers.schemas import CustomerCreate, CustomerOut
from app.modules.customers.service import create, get

router = APIRouter()

@router.post("", response_model=CustomerOut)
def create_customer(payload: CustomerCreate):
    return create(payload.model_dump())

@router.get("/{customer_id}", response_model=CustomerOut)
def read_customer(customer_id: str):
    row = get(customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row

