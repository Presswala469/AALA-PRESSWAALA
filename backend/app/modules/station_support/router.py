from fastapi import APIRouter, Depends, HTTPException
from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role, enforce_station_access, current_user_id
from app.modules.station_support.schemas import SupportRequestCreate, SupportStatusUpdate
from app.modules.station_support import service

router=APIRouter()
_STATION_ROLES=(UserRole.SUPER_ADMIN,UserRole.ADMIN,UserRole.STATION_MANAGER)

@router.post('',response_model=dict,dependencies=[Depends(require_role(*_STATION_ROLES))])
def create(payload: SupportRequestCreate, claims=Depends(current_claims)):
    enforce_station_access(payload.station_code,claims)
    return service.create(payload.model_dump(), current_user_id(claims))

@router.get('/{station_code}',response_model=list,dependencies=[Depends(require_role(*_STATION_ROLES))])
def list_requests(station_code:str,claims=Depends(current_claims)):
    enforce_station_access(station_code,claims)
    return service.list_for_station(station_code)

@router.patch('/{request_id}',response_model=dict,dependencies=[Depends(require_role(*_STATION_ROLES))])
def update(request_id:str,payload:SupportStatusUpdate,claims=Depends(current_claims)):
    # Determine station from the request before enforcing isolation.
    row=None
    from app.modules.station_support import repository as repo
    if not repo.settings.database_url:
        row=repo._requests.get(request_id)
    else:
        with repo.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('select station_code from station_support_requests where request_id=%s',(request_id,)); r=cur.fetchone()
                if r: row={'station_code':r[0]}
    if not row: raise HTTPException(404,'Support request not found')
    enforce_station_access(row['station_code'],claims)
    updated=service.update(request_id,payload.status,current_user_id(claims))
    return updated
