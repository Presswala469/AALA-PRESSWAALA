from fastapi import APIRouter, HTTPException
from app.modules.complaints.schemas import ComplaintCreate, ComplaintStatusUpdate
from app.modules.complaints import service
router=APIRouter()
@router.post('',response_model=dict)
def create(payload:ComplaintCreate):
    try:return service.create(payload.model_dump())
    except ValueError as e: raise HTTPException(400,str(e))
@router.patch('/{complaint_id}',response_model=dict)
def update(complaint_id,payload:ComplaintStatusUpdate):
    try:return service.update(complaint_id,payload.model_dump())
    except ValueError as e: raise HTTPException(400,str(e))
@router.get('/{complaint_id}',response_model=dict)
def get(complaint_id): return service.get(complaint_id) or {}
@router.get('/{complaint_id}/events',response_model=list)
def events(complaint_id): return service.events(complaint_id)

