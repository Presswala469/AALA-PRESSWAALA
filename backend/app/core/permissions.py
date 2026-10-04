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
}


def current_claims(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        claims = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

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


def current_partner_id(claims: dict) -> str | None:
    """Resolve the authenticated partner's partner_id from server-side identity."""
    if claims.get("role") != UserRole.PARTNER.value:
        return None
    if not settings.database_url:
        from app.modules.partners.repository import _partners
        mobile = claims.get("sub")
        for partner_id, row in _partners.items():
            if row.get("mobile_number") == mobile and row.get("active", True):
                return partner_id
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner identity not linked")
    from app.core.database import get_connection
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """select id
                   from partners
                  where user_id=(select id from users where mobile_number=%s)
                    and lower(coalesce(status,'')) in ('active','enabled')
                  limit 1""",
                (claims.get("sub"),),
            )
            row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner identity not linked")
    return row[0]


def enforce_partner_identity(partner_id: str, claims: dict) -> str:
    """For partner sessions, reject any caller-supplied partner_id that differs from identity."""
    if claims.get("role") == UserRole.PARTNER.value:
        resolved = current_partner_id(claims)
        if resolved != partner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner access denied")
    return partner_id



def current_user_id(claims: dict) -> str | None:
    mobile=claims.get('sub')
    if not settings.database_url:
        return mobile
    from app.core.database import get_connection
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select id from users where mobile_number=%s',(mobile,))
            row=cur.fetchone()
    return str(row[0]) if row else None

def current_customer_id(claims: dict) -> str | None:
    """Resolve the authenticated customer's stable customer_id from server-side identity."""
    if claims.get("role") != UserRole.CUSTOMER.value:
        return None
    mobile = claims.get("sub")
    if not settings.database_url:
        from app.modules.customers.repository import _customers
        for cid, row in reversed(list(_customers.items())):
            if row.get("mobile_number") == mobile:
                return cid
        return None
    from app.core.database import get_connection
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""select customer_id from customers
                           where user_id=(select id from users where mobile_number=%s)
                              or mobile_number=%s
                           order by case when user_id is not null then 0 else 1 end
                           limit 1""", (mobile, mobile))
            row = cur.fetchone()
    return row[0] if row else None


def enforce_customer_identity(customer_id: str, claims: dict) -> str:
    """Customers may access only their own customer-scoped objects."""
    if claims.get("role") == UserRole.CUSTOMER.value:
        resolved = current_customer_id(claims)
        if not resolved or resolved != customer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customer access denied")
    return customer_id

def enforce_station_access(station_code: str, claims: dict) -> str:
    """Enforce station isolation for Station Managers; admins retain global access."""
    role = claims.get("role")
    if role in {UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value}:
        return station_code
    if role != UserRole.STATION_MANAGER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Station access denied")

    if settings.database_url:
        from app.core.database import get_connection
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """select 1
                       from user_station_assignments usa
                       join users u on u.id=usa.user_id
                      where u.mobile_number=%s and usa.station_code=%s and usa.active=true
                      limit 1""",
                    (claims.get("sub"), station_code),
                )
                if cur.fetchone():
                    return station_code
    else:
        # Development fallback: station assignments may be seeded in-memory by tests.
        assignments = getattr(enforce_station_access, "_dev_assignments", set())
        if (claims.get("sub"), station_code) in assignments:
            return station_code

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Station access denied")


def enforce_partner_station(partner_id: str, station_code: str, claims: dict) -> str:
    """Require an authenticated partner to be assigned to the target station."""
    enforce_partner_identity(partner_id, claims)
    if claims.get("role") != UserRole.PARTNER.value:
        return station_code

    if settings.database_url:
        from app.core.database import get_connection
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """select 1
                       from partner_station_assignments a
                       join stations s on s.id=a.station_id
                      where a.partner_id=%s
                        and s.station_code=%s
                        and a.is_active=true
                      limit 1""",
                    (partner_id, station_code),
                )
                if cur.fetchone():
                    return station_code
    else:
        assignments = getattr(enforce_partner_station, "_dev_assignments", set())
        if (partner_id, station_code) in assignments:
            return station_code

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Partner is not assigned to this station")


def enforce_station_order_access(order_id: str, claims: dict) -> str | None:
    """Resolve an order's station and enforce Station Manager isolation for order-level reads."""
    role = claims.get("role")
    if role in {UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value}:
        return None
    if role != UserRole.STATION_MANAGER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Station access denied")

    station_code = None
    if settings.database_url:
        from app.core.database import get_connection
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """select station_code from station_status_history
                       where order_id=%s order by created_at desc limit 1""",
                    (order_id,),
                )
                row = cur.fetchone()
                if row:
                    station_code = row[0]
                else:
                    cur.execute("select station_code from station_receiving where order_id=%s limit 1", (order_id,))
                    row = cur.fetchone()
                    if row:
                        station_code = row[0]
                    else:
                        cur.execute("select station_code from station_arrivals where order_id=%s order by arrived_at desc limit 1", (order_id,))
                        row = cur.fetchone()
                        if row:
                            station_code = row[0]
    else:
        from app.modules.station_operations import repository as station_repo
        row = station_repo._status.get(order_id) or station_repo._receipts.get(order_id) or station_repo._arrivals.get(order_id)
        station_code = row.get("station_code") if row else None

    if not station_code:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Station access cannot be resolved")
    enforce_station_access(station_code, claims)
    return station_code
