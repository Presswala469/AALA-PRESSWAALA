from fastapi import APIRouter, Depends
from app.core.constants import UserRole
from app.core.permissions import require_role
from app.core.config import settings
router=APIRouter()
@router.get('/readiness',dependencies=[Depends(require_role(UserRole.SUPER_ADMIN,UserRole.ADMIN))])
def readiness():
    checks={'database_configured':bool(settings.database_url),'jwt_secret_configured':settings.jwt_secret!='CHANGE_ME_IN_ENV','supabase_configured':bool(settings.supabase_url and settings.supabase_service_key),'s3_configured':bool(settings.aws_s3_bucket),'firebase_configured':bool(settings.firebase_project_id),'razorpay_configured':bool(settings.razorpay_key_id and settings.razorpay_key_secret),'maps_configured':bool(settings.google_maps_api_key)}
    return {'ready':all(checks.values()),'checks':checks,'environment':settings.environment}
