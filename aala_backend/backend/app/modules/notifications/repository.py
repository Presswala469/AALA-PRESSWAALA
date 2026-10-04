from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
import json
from app.core.config import settings
from app.core.database import get_connection

_notifications = {}

def now():
    return datetime.now(timezone.utc).isoformat()

def create(data):
    nid = data.get("notification_id") or f"NTF-{uuid4().hex[:10].upper()}"
    row = {**deepcopy(data), "notification_id": nid, "status": data.get("status", "QUEUED"), "created_at": now()}
    if not settings.database_url:
        _notifications[nid] = row
        return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "insert into notifications(notification_id,recipient_id,channel,title,message,data,status) "
                "values(%s,%s,%s,%s,%s,%s::jsonb,%s) returning created_at",
                (nid, data["recipient_id"], data["channel"], data["title"], data["message"],
                 json.dumps(data.get("data") or {}), row["status"])
            )
            row["created_at"] = cur.fetchone()[0].isoformat()
            conn.commit()
    return row

def update(nid, status, **values):
    if not settings.database_url:
        if nid not in _notifications:
            return None
        _notifications[nid].update(values, status=status, updated_at=now())
        return deepcopy(_notifications[nid])
    with get_connection() as conn:
        with conn.cursor() as cur:
            sets = ["status=%s", "updated_at=now()"]
            params = [status]
            for key, value in values.items():
                if key not in {"data", "title", "message"}:
                    continue
                sets.append(f"{key}=%s")
                params.append(value)
            params.append(nid)
            cur.execute(f"update notifications set {', '.join(sets)} where notification_id=%s", params)
            if cur.rowcount == 0:
                conn.rollback()
                return None
            cur.execute(
                "select notification_id,recipient_id,channel,title,message,data,status,created_at,updated_at "
                "from notifications where notification_id=%s", (nid,)
            )
            r = cur.fetchone()
            conn.commit()
    keys=("notification_id","recipient_id","channel","title","message","data","status","created_at","updated_at")
    return dict(zip(keys,r))

def for_recipient(recipient_id):
    if not settings.database_url:
        return [deepcopy(x) for x in _notifications.values() if x["recipient_id"] == recipient_id]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "select notification_id,recipient_id,channel,title,message,data,status,created_at,updated_at "
                "from notifications where recipient_id=%s order by created_at desc", (recipient_id,)
            )
            rows=cur.fetchall()
    keys=("notification_id","recipient_id","channel","title","message","data","status","created_at","updated_at")
    return [dict(zip(keys,r)) for r in rows]
