from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
import hashlib, json
from app.core.config import settings
from app.core.database import get_connection

_notifications = {}
_devices = {}
_preferences = {}
_attempts = []

def now():
    return datetime.now(timezone.utc).isoformat()

def _audit(actor_user_id, action, entity_type, entity_id, new_values=None, old_values=None):
    if not settings.database_url or not actor_user_id:
        return
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "insert into audit_logs(actor_user_id,action,entity_type,entity_id,old_values,new_values) "
                "values(%s,%s,%s,%s,%s::jsonb,%s::jsonb)",
                (actor_user_id, action, entity_type, entity_id,
                 json.dumps(old_values) if old_values is not None else None,
                 json.dumps(new_values) if new_values is not None else None),
            )
        conn.commit()

def create(data, actor_user_id=None):
    nid = data.get("notification_id") or f"NTF-{uuid4().hex[:10].upper()}"
    row = {**deepcopy(data), "notification_id": nid, "status": data.get("status","QUEUED"),
           "attempt_count": 0, "created_at": now()}
    if not settings.database_url:
        key=data.get("idempotency_key")
        if key:
            for x in _notifications.values():
                if x.get("idempotency_key")==key:
                    return deepcopy(x)
        _notifications[nid]=row
        return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            if data.get("idempotency_key"):
                cur.execute("select notification_id,recipient_id,channel,title,message,data,status,created_at,updated_at,event_type,idempotency_key,priority,provider,provider_message_id,attempt_count,failure_code,failure_reason,sent_at,delivered_at,read_at from notifications where idempotency_key=%s", (data["idempotency_key"],))
                existing=cur.fetchone()
                if existing:
                    return _row(existing)
            cur.execute(
                "insert into notifications(notification_id,recipient_id,channel,title,message,data,status,event_type,idempotency_key,priority,provider,attempt_count) "
                "values(%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,0) "
                "returning notification_id,recipient_id,channel,title,message,data,status,created_at,updated_at,event_type,idempotency_key,priority,provider,provider_message_id,attempt_count,failure_code,failure_reason,sent_at,delivered_at,read_at",
                (nid,data["recipient_id"],data["channel"],data["title"],data["message"],json.dumps(data.get("data") or {}),
                 row["status"],data.get("event_type"),data.get("idempotency_key"),data.get("priority","NORMAL"),data.get("provider")))
            r=cur.fetchone(); conn.commit()
    result=_row(r)
    _audit(actor_user_id,"create","notification",None,new_values={"notification_id":nid,"recipient_id":data["recipient_id"],"channel":data["channel"],"event_type":data.get("event_type")})
    return result

def _row(r):
    keys=("notification_id","recipient_id","channel","title","message","data","status","created_at","updated_at","event_type","idempotency_key","priority","provider","provider_message_id","attempt_count","failure_code","failure_reason","sent_at","delivered_at","read_at")
    return dict(zip(keys,r))

def update(nid,status,actor_user_id=None,**values):
    if status not in {"QUEUED","SENT","DELIVERED","FAILED","READ"}:
        raise ValueError("Invalid notification status")
    if not settings.database_url:
        if nid not in _notifications: return None
        _notifications[nid].update(values,status=status,updated_at=now())
        return deepcopy(_notifications[nid])
    allowed={"data","title","message","provider","provider_message_id","attempt_count","failure_code","failure_reason","sent_at","delivered_at","read_at"}
    with get_connection() as conn:
        with conn.cursor() as cur:
            sets=["status=%s","updated_at=now()"]; params=[status]
            for k,v in values.items():
                if k in allowed: sets.append(f"{k}=%s"); params.append(v)
            params.append(nid)
            cur.execute(f"update notifications set {', '.join(sets)} where notification_id=%s",params)
            if not cur.rowcount:
                conn.rollback(); return None
            cur.execute("select notification_id,recipient_id,channel,title,message,data,status,created_at,updated_at,event_type,idempotency_key,priority,provider,provider_message_id,attempt_count,failure_code,failure_reason,sent_at,delivered_at,read_at from notifications where notification_id=%s",(nid,))
            r=cur.fetchone(); conn.commit()
    result=_row(r)
    _audit(actor_user_id,"update","notification",None,new_values={"notification_id":nid,"status":status})
    return result

def get(nid):
    if not settings.database_url:
        return deepcopy(_notifications.get(nid)) if nid in _notifications else None
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select notification_id,recipient_id,channel,title,message,data,status,created_at,updated_at,event_type,idempotency_key,priority,provider,provider_message_id,attempt_count,failure_code,failure_reason,sent_at,delivered_at,read_at from notifications where notification_id=%s",(nid,))
            r=cur.fetchone()
    return _row(r) if r else None

def for_recipient(recipient_id):
    if not settings.database_url:
        return sorted([deepcopy(x) for x in _notifications.values() if x["recipient_id"]==recipient_id],
                      key=lambda x:x["created_at"], reverse=True)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select notification_id,recipient_id,channel,title,message,data,status,created_at,updated_at,event_type,idempotency_key,priority,provider,provider_message_id,attempt_count,failure_code,failure_reason,sent_at,delivered_at,read_at from notifications where recipient_id=%s order by created_at desc",(recipient_id,))
            rows=cur.fetchall()
    return [_row(r) for r in rows]

def register_device(user_id,platform,token,installation_id=None,device_id=None,app_version=None,actor_user_id=None):
    row={"user_id":user_id,"platform":platform,"token":token,"installation_id":installation_id,"device_id":device_id,"app_version":app_version,"active":True,"last_seen_at":now()}
    if not settings.database_url:
        _devices[token]=row; return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "insert into notification_devices(user_id,platform,token,installation_id,device_id,app_version,active,last_seen_at,updated_at) "
                "values(%s,%s,%s,%s,%s,%s,true,now(),now()) "
                "on conflict(token) do update set user_id=excluded.user_id,platform=excluded.platform,installation_id=excluded.installation_id,device_id=excluded.device_id,app_version=excluded.app_version,active=true,last_seen_at=now(),updated_at=now() "
                "returning id,user_id,platform,token,installation_id,device_id,app_version,active,last_seen_at",
                (user_id,platform,token,installation_id,device_id,app_version))
            r=cur.fetchone(); conn.commit()
    result=dict(zip(("id","user_id","platform","token","installation_id","device_id","app_version","active","last_seen_at"),r))
    _audit(actor_user_id,"create","notification_device",result["id"],new_values={"user_id":user_id,"platform":platform})
    return result

def deactivate_device(token, actor_user_id=None):
    if not settings.database_url:
        if token in _devices: _devices[token]["active"]=False; return True
        return False
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("update notification_devices set active=false,updated_at=now() where token=%s",(token,))
            ok=cur.rowcount>0; conn.commit()
    if ok: _audit(actor_user_id,"update","notification_device",None,new_values={"token_hash":hashlib.sha256(token.encode()).hexdigest(),"active":False})
    return ok

def get_device_owner(token):
    if not settings.database_url:
        row=_devices.get(token); return row.get("user_id") if row else None
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select user_id from notification_devices where token=%s",(token,))
            row=cur.fetchone()
    return str(row[0]) if row else None

def active_tokens(user_id):
    if not settings.database_url:
        return [x["token"] for x in _devices.values() if x["user_id"]==user_id and x["active"]]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select token from notification_devices where user_id=%s and active=true order by last_seen_at desc",(user_id,))
            return [r[0] for r in cur.fetchall()]

def deactivate_token(token):
    if not settings.database_url:
        if token in _devices: _devices[token]["active"]=False
        return
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("update notification_devices set active=false,updated_at=now() where token=%s",(token,))
        conn.commit()

def get_preferences(user_id,event_type=None):
    if not settings.database_url:
        vals=[deepcopy(v) for v in _preferences.values() if v["user_id"]==user_id]
        return [v for v in vals if event_type is None or v["event_type"]==event_type]
    with get_connection() as conn:
        with conn.cursor() as cur:
            if event_type:
                cur.execute("select id,user_id,event_type,channel,enabled,updated_at from notification_preferences where user_id=%s and event_type=%s",(user_id,event_type))
            else:
                cur.execute("select id,user_id,event_type,channel,enabled,updated_at from notification_preferences where user_id=%s order by event_type,channel",(user_id,))
            rows=cur.fetchall()
    return [dict(zip(("id","user_id","event_type","channel","enabled","updated_at"),r)) for r in rows]

def set_preference(user_id,event_type,channel,enabled,actor_user_id=None):
    if not settings.database_url:
        key=(user_id,event_type,channel)
        _preferences[key]={"user_id":user_id,"event_type":event_type,"channel":channel,"enabled":enabled,"updated_at":now()}
        return deepcopy(_preferences[key])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "insert into notification_preferences(user_id,event_type,channel,enabled,updated_at) values(%s,%s,%s,%s,now()) "
                "on conflict(user_id,event_type,channel) do update set enabled=excluded.enabled,updated_at=now() "
                "returning id,user_id,event_type,channel,enabled,updated_at",(user_id,event_type,channel,enabled))
            r=cur.fetchone(); conn.commit()
    result=dict(zip(("id","user_id","event_type","channel","enabled","updated_at"),r))
    _audit(actor_user_id,"update","notification_preference",result["id"],new_values={"user_id":user_id,"event_type":event_type,"channel":channel,"enabled":enabled})
    return result

def allowed_channels(user_id,event_type,default_channels):
    prefs={p["channel"]:p["enabled"] for p in get_preferences(user_id,event_type)}
    return [c for c in default_channels if prefs.get(c,True)]

def next_attempt_no(nid):
    if not settings.database_url:
        return sum(1 for x in _attempts if x["notification_id"]==nid)+1
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select coalesce(max(attempt_no),0)+1 from notification_attempts where notification_id=%s",(nid,))
            n=cur.fetchone()[0]
    return n

def add_attempt(nid,attempt_no,provider,status,message_id=None,error_code=None,error_message=None,target_token=None):
    item={"notification_id":nid,"attempt_no":attempt_no,"provider":provider,"status":status,
          "provider_message_id":message_id,"error_code":error_code,"error_message":error_message,
          "target_token_hash":hashlib.sha256(target_token.encode()).hexdigest() if target_token else None,"attempted_at":now()}
    if not settings.database_url:
        _attempts.append(item); return deepcopy(item)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into notification_attempts(notification_id,attempt_no,target_token_hash,provider,status,provider_message_id,error_code,error_message) values(%s,%s,%s,%s,%s,%s,%s,%s) on conflict(notification_id,attempt_no) do nothing",
                        (nid,attempt_no,item["target_token_hash"],provider,status,message_id,error_code,error_message))
        conn.commit()
    return deepcopy(item)
