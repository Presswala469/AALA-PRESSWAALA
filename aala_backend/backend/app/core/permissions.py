from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.core.config import settings
from app.core.constants import UserRole

bearer = HTTPBearer(auto_error=False)

PERMISSIONS: dict[str, set[UserRole]] = {
    "company.read": {UserRole.SUPER_ADMIN, UserRole.ADMIN},
    "company.manage": {UserRole.SUPER_ADMIN},
    "customer.read": {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STATION_MANAGER},
    "customer.manage": {UserRole.SUPER_ADMIN, UserRole.ADMIN},
    "inventory.read": {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STATION_MANAGER},
    "inventory.manage": {UserRole.SUPER_ADMIN, UserRole.ADMIN},
    "audit.read": {UserRole.SUPER_ADMIN, UserRole.ADMIN},
    "company.documents.manage": {UserRole.SUPER_ADMIN},
    "invoice.read": {UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.STATION_MANAGER, UserRole.CUSTOMER},
    "invoice.manage": {UserRole.SUPER_ADMIN, UserRole.ADMIN},
}

def current_claims(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        claims = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    # JWT validity alone is not enough: logout/revocation must take effect immediately.
    if settings.database_url:
        from app.core.database import get_connection
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "select revoked_at, expires_at from sessions where id=%s",
                    (claims.get("sid"),),
                )
                row = cur.fetchone()
        if not row or row[0] is not None or row[1] <= __import__("datetime").datetime.now(__import__("datetime").timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or revoked")
    return claims

def require_role(*roles: UserRole):
    allowed = {role.value for role in roles}
    def dependency(claims=Depends(current_claims)):
        if claims.get("role") not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return claims
    return dependency

def role_has_permission(role: UserRole, permission: str) -> bool:
    return role in PERMISSIONS.get(permission, set())
