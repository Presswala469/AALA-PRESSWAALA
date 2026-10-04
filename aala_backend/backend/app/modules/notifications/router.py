from fastapi import APIRouter, HTTPException
from app.modules.notifications.schemas import NotificationCreate
from app.modules.notifications import service
router=APIRouter()
@router.post('',response_model=dict)
def queue(payload:NotificationCreate): return service.queue(payload.model_dump())
@router.patch('/{notification_id}/{status}',response_model=dict)
def mark(notification_id,status):
    try:return service.mark(notification_id,status)
    except ValueError as e: raise HTTPException(400,str(e))
@router.get('/recipient/{recipient_id}',response_model=list)
def recipient(recipient_id): return service.list_for_recipient(recipient_id)

