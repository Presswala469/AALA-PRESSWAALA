from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
import json
from app.core.config import settings
from app.core.database import get_connection

_hangers = {}; _returns = {}; _movements = []

def now(): return datetime.now(timezone.utc).isoformat()

def create(data):
    hid = data.get("hanger_id") or f"HNG-{uuid4().hex[:10].upper()}"
    row = {**deepcopy(data), "hanger_id": hid, "status": data.get("status","ISSUED"), "created_at": now(), "pending_since": now() if data.get("status","ISSUED")=="PENDING" else None}
    if not settings.database_url:
        _hangers[hid] = row
        _movements.append({"hanger_id":hid,"action":"CREATED","created_at":now()})
        return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "insert into hangers(hanger_id,customer_id,order_id,quantity,status,pending_since) values(%s,%s,%s,%s,%s,case when %s='PENDING' then now() else null end) returning created_at",
                (hid,data["customer_id"],data.get("order_id"),data.get("quantity",1),row["status"],row["status"])
            )
            row["created_at"]=cur.fetchone()[0].isoformat()
            cur.execute("insert into hanger_movements(hanger_id,action,actor,remarks) values(%s,%s,%s,%s)",
                        (hid,"CREATED",data.get("actor"),data.get("remarks")))
            conn.commit()
    return row

def update(hid,status,actor=None,remarks=None):
    if not settings.database_url:
        if hid not in _hangers:return None
        _hangers[hid].update(status=status,updated_at=now())
        _movements.append({"hanger_id":hid,"action":status,"actor":actor,"remarks":remarks,"created_at":now()})
        return deepcopy(_hangers[hid])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("update hangers set status=%s, updated_at=now(), pending_since=case when %s='PENDING' then coalesce(pending_since,now()) else null end where hanger_id=%s",(status,status,hid))
            if cur.rowcount==0: conn.rollback(); return None
            cur.execute("insert into hanger_movements(hanger_id,action,actor,remarks) values(%s,%s,%s,%s)",(hid,status,actor,remarks))
            cur.execute("select hanger_id,customer_id,order_id,quantity,status,created_at,updated_at,pending_since from hangers where hanger_id=%s",(hid,))
            r=cur.fetchone(); conn.commit()
    return dict(zip(("hanger_id","customer_id","order_id","quantity","status","created_at","updated_at","pending_since"),r))

def get(hid):
    if not settings.database_url:return deepcopy(_hangers.get(hid))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select hanger_id,customer_id,order_id,quantity,status,created_at,updated_at,pending_since from hangers where hanger_id=%s",(hid,))
            r=cur.fetchone()
    return dict(zip(("hanger_id","customer_id","order_id","quantity","status","created_at","updated_at","pending_since"),r)) if r else None

def for_customer(customer_id):
    if not settings.database_url:return [deepcopy(x) for x in _hangers.values() if x.get("customer_id")==customer_id]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select hanger_id,customer_id,order_id,quantity,status,created_at,updated_at,pending_since from hangers where customer_id=%s order by created_at desc",(customer_id,))
            rows=cur.fetchall()
    keys=("hanger_id","customer_id","order_id","quantity","status","created_at","updated_at","pending_since")
    return [dict(zip(keys,r)) for r in rows]

def create_return(data):
    rid=f"HRR-{uuid4().hex[:10].upper()}"
    row={**deepcopy(data),"return_request_id":rid,"status":"REQUESTED","created_at":now()}
    if not settings.database_url:
        _returns[rid]=row; return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into hanger_return_requests(return_request_id,customer_id,address_id,quantity,preferred_slot_id,status) values(%s,%s,%s,%s,%s,%s) returning created_at",
                        (rid,data["customer_id"],data["address_id"],data["quantity"],data.get("preferred_slot_id"),"REQUESTED"))
            row["created_at"]=cur.fetchone()[0].isoformat(); conn.commit()
    return row

def returns(customer_id):
    if not settings.database_url:return [deepcopy(x) for x in _returns.values() if x.get("customer_id")==customer_id]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select return_request_id,customer_id,address_id,quantity,preferred_slot_id,status,created_at from hanger_return_requests where customer_id=%s order by created_at desc",(customer_id,))
            rows=cur.fetchall()
    keys=("return_request_id","customer_id","address_id","quantity","preferred_slot_id","status","created_at")
    return [dict(zip(keys,r)) for r in rows]
