from datetime import datetime, timedelta, timezone
from uuid import uuid4
import hashlib
import jwt

from app.core.config import settings
from app.core.database import get_connection

_otps: dict[str, str] = {}
_dev_sessions: dict[str, dict] = {}


def _token(mobile_number: str, role: str, session_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": mobile_number,
        "role": role,
        "sid": session_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def request_otp(mobile_number: str) -> dict:
    # Development-only deterministic OTP. Production provider integration replaces this.
    _otps[mobile_number] = "123456"
    response = {"accepted": True, "message": "OTP generated"}
    if settings.environment != "production":
        response["development_otp"] = "123456"
    return response


def verify_otp(mobile_number: str, otp: str, device_id: str | None = None, platform: str | None = None) -> dict:
    if _otps.get(mobile_number) != otp:
        raise ValueError("Invalid OTP")
    session_id = str(uuid4())
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    if settings.database_url:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    insert into users(mobile_number, mobile_verified_at)
                    values (%s, now())
                    on conflict (mobile_number) do update set mobile_verified_at=now(), updated_at=now()
                    returning id
                """, (mobile_number,))
                user_id = cur.fetchone()[0]
                cur.execute("select id from roles where code='customer'")
                customer_role_id = cur.fetchone()[0]
                cur.execute("insert into user_roles(user_id, role_id) values (%s,%s) on conflict do nothing", (user_id, customer_role_id))
                cur.execute("select r.code from user_roles ur join roles r on r.id=ur.role_id where ur.user_id=%s order by case r.code when 'super_admin' then 1 when 'admin' then 2 when 'station_manager' then 3 when 'partner' then 4 else 5 end limit 1", (user_id,))
                role_row = cur.fetchone()
                role = role_row[0] if role_row else 'customer'
                cur.execute("insert into sessions(id,user_id,device_id,platform,expires_at) values (%s,%s,%s,%s,%s)", (session_id,user_id,device_id,platform,expires))
                conn.commit()
    else:
        _dev_sessions[session_id] = {"mobile": mobile_number, "expires_at": expires, "revoked": False}
    return {"access_token": _token(mobile_number, role if settings.database_url else "customer", session_id), "session_id": session_id, "token_type": "bearer"}


def revoke_session(session_id: str) -> None:
    if settings.database_url:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("update sessions set revoked_at=now() where id=%s", (session_id,))
            conn.commit()
    elif session_id in _dev_sessions:
        _dev_sessions[session_id]["revoked"] = True

