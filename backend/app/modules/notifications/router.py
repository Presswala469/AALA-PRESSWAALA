from fastapi import APIRouter, HTTPException, Depends
from app.modules.notifications.schemas import NotificationCreate, NotificationEvent, DeviceRegister, PreferenceUpdate
from app.modules.notifications import service
from app.core.permissions import require_role, current_claims
from app.core.constants import UserRole
from app.core.config import settings
from app.core.database import get_connection

router=APIRouter()
_any_role=Depends(require_role(UserRole.SUPER_ADMIN,UserRole.ADMIN,UserRole.STATION_MANAGER,UserRole.PARTNER,UserRole.CUSTOMER))
_admin=Depends(require_role(UserRole.SUPER_ADMIN,UserRole.ADMIN))

def _claims_user_id(claims):
    if not settings.database_url:
        return claims.get("sub")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select id from users where mobile_number=%s",(claims.get("sub"),))
            row=cur.fetchone()
    if not row:
        raise HTTPException(401,"Authenticated user not found")
    return str(row[0])

def _target_user_id(claims, requested):
    role=claims.get("role")
    own=_claims_user_id(claims)
    if role in {UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value}:
        return requested or own
    if requested and str(requested) != own:
        raise HTTPException(403,"Cannot manage another user's notification data")
    return own

@router.post("",response_model=dict, dependencies=[_admin])
def queue(payload:NotificationCreate, claims=Depends(current_claims)):
    return service.queue(payload.model_dump(), actor_user_id=_claims_user_id(claims))

@router.post("/events",response_model=list, dependencies=[_admin])
def dispatch(payload:NotificationEvent, claims=Depends(current_claims)):
    return service.dispatch_event(payload.model_dump(), actor_user_id=_claims_user_id(claims))

@router.post("/devices",response_model=dict, dependencies=[_any_role])
def register_device(payload:DeviceRegister, claims=Depends(current_claims)):
    uid=_target_user_id(claims,payload.user_id)
    data=payload.model_dump()
    data["user_id"]=uid
    return service.register_device(data, actor_user_id=uid)

@router.delete("/devices/{token}",response_model=dict, dependencies=[_any_role])
def deactivate_device(token:str, claims=Depends(current_claims)):
    # Non-admin users can only deactivate a token owned by their own account.
    uid=_claims_user_id(claims)
    if claims.get("role") not in {UserRole.SUPER_ADMIN.value,UserRole.ADMIN.value}:
        owned=service.get_device_owner(token)
        if owned and owned != uid: raise HTTPException(403,"Cannot deactivate another user's device")
    return {"deactivated":service.deactivate_device(token, actor_user_id=uid)}

@router.get("/preferences",response_model=list, dependencies=[_any_role])
def preferences(claims=Depends(current_claims)):
    return service.get_preferences(_claims_user_id(claims))

@router.put("/preferences",response_model=dict, dependencies=[_any_role])
def set_preference(payload:PreferenceUpdate, claims=Depends(current_claims)):
    uid=_claims_user_id(claims)
    return service.set_preference({"user_id":uid,**payload.model_dump()}, actor_user_id=uid)

@router.patch("/{notification_id}/read",response_model=dict, dependencies=[_any_role])
def mark_read(notification_id:str, claims=Depends(current_claims)):
    uid=_claims_user_id(claims)
    item=service.get(notification_id)
    if not item: raise HTTPException(404,"Notification not found")
    if claims.get("role") not in {UserRole.SUPER_ADMIN.value,UserRole.ADMIN.value} and item["recipient_id"] != uid:
        raise HTTPException(403,"Cannot modify another user's notification")
    result=service.mark(notification_id,"READ",actor_user_id=uid)
    if not result: raise HTTPException(404,"Notification not found")
    return result

@router.post("/{notification_id}/send",response_model=dict, dependencies=[_admin])
def send(notification_id:str):
    result=service.send(notification_id)
    if not result: raise HTTPException(404,"Notification not found")
    return result

@router.patch("/{notification_id}/{status}",response_model=dict, dependencies=[_admin])
def mark(notification_id,status,claims=Depends(current_claims)):
    try:
        result=service.mark(notification_id,status,actor_user_id=_claims_user_id(claims))
        if not result: raise HTTPException(404,"Notification not found")
        return result
    except ValueError as e: raise HTTPException(400,str(e))

@router.get("/recipient/{recipient_id}",response_model=list, dependencies=[_any_role])
def recipient(recipient_id,claims=Depends(current_claims)):
    uid=_claims_user_id(claims)
    if claims.get("role") not in {UserRole.SUPER_ADMIN.value,UserRole.ADMIN.value} and recipient_id != uid:
        raise HTTPException(403,"Cannot read another user's notifications")
    return service.list_for_recipient(recipient_id)
