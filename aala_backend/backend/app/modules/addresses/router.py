from fastapi import APIRouter
from app.modules.addresses.schemas import AddressCreate
from app.modules.addresses.service import create, list_current_and_history

router = APIRouter()

@router.post("")
def create_address(payload: AddressCreate):
    return create(payload.model_dump())

@router.get("/customer/{customer_id}")
def list_addresses(customer_id: str):
    return list_current_and_history(customer_id)

