from fastapi import APIRouter, Depends

from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from app.modules.notifications import service
from app.modules.notifications.schemas import NotificationCreate

router = APIRouter()

_AUTH = Depends(current_claims)
_ADMIN = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))


@router.post("", response_model=dict, dependencies=[_ADMIN])
def create(payload: NotificationCreate):
    return service.queue(payload.model_dump())


@router.patch("/{notification_id}/{status}", response_model=dict, dependencies=[_ADMIN])
def mark(notification_id: str, status: str):
    return service.mark(notification_id, status)


@router.get("/recipient/{recipient_id}", response_model=list, dependencies=[_AUTH])
def recipient(recipient_id: str):
    return service.list_for_recipient(recipient_id)
