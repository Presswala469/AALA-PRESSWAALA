from copy import deepcopy
from datetime import datetime, timezone
from app.core.config import settings
from app.core.database import get_connection

_arrivals = {}; _receipts = {}; _status = {}; _evidence = {}; _history = {}

def now(): return datetime.now(timezone.utc).isoformat()
def put(store, key, data): store[key] = deepcopy(data); return deepcopy(data)
def get(store, key): return deepcopy(store.get(key))

def add_history(order_id, data):
    _history.setdefault(order_id, []).append(deepcopy(data))
    return deepcopy(data)

def list_history(order_id): return deepcopy(_history.get(order_id, []))

def save_arrival(order_id, data):
    if not settings.database_url: return put(_arrivals, order_id, data)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""insert into station_arrivals(order_id,partner_id,station_code,latitude,longitude,arrived_at)
                values(%s,%s,%s,%s,%s,%s) returning id,arrived_at""", (order_id,data['partner_id'],data['station_code'],data['latitude'],data['longitude'],data['arrived_at']))
            row=cur.fetchone(); conn.commit()
    return {**data,'id':row[0],'arrived_at':row[1].isoformat() if hasattr(row[1],'isoformat') else str(row[1])}

def save_receipt(order_id, data):
    if not settings.database_url: return put(_receipts, order_id, data)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""insert into station_receiving(order_id,partner_id,station_code,partner_handover_quantity,station_received_quantity,discrepancy,reason,remarks)
                values(%s,%s,%s,%s,%s,%s,%s,%s)
                on conflict(order_id) do update set partner_handover_quantity=excluded.partner_handover_quantity,
                station_received_quantity=excluded.station_received_quantity,discrepancy=excluded.discrepancy,reason=excluded.reason,remarks=excluded.remarks,received_at=now()
                returning order_id,received_at""", (order_id,data['partner_id'],data['station_code'],data['partner_handover_quantity'],data['station_received_quantity'],data['discrepancy'],data.get('reason'),data.get('remarks')))
            row=cur.fetchone(); conn.commit()
    return {**data,'order_id':row[0],'received_at':row[1].isoformat() if hasattr(row[1],'isoformat') else str(row[1])}

def save_status(order_id, data):
    if not settings.database_url: return put(_status, order_id, data)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into station_status_history(order_id,station_code,status,reason,remarks,actor) values(%s,%s,%s,%s,%s,%s) returning created_at",(order_id,data['station_code'],data['status'],data.get('reason'),data.get('remarks'),data.get('actor')))
            created=cur.fetchone()[0]; conn.commit()
    return {**data,'created_at':created.isoformat() if hasattr(created,'isoformat') else str(created)}

def save_evidence(order_id,data):
    if not settings.database_url: return put(_evidence, f"{order_id}:{len(_evidence)}", data)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into station_evidence(order_id,station_code,evidence_type,evidence_url,remarks,actor) values(%s,%s,%s,%s,%s,%s) returning id,created_at",(order_id,data['station_code'],data['evidence_type'],data['evidence_url'],data.get('remarks'),data.get('actor')))
            row=cur.fetchone(); conn.commit()
    return {**data,'id':row[0],'created_at':row[1].isoformat() if hasattr(row[1],'isoformat') else str(row[1])}

def list_incoming(station_code, statuses):
    if not settings.database_url:
        return [deepcopy(v) for v in _status.values() if v.get('station_code')==station_code and v.get('status') in statuses]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""select order_id,status,reason,remarks,created_at from station_status_history s
                where station_code=%s and status = any(%s) order by created_at desc""",(station_code,statuses)); rows=cur.fetchall()
    return [dict(zip(('order_id','status','reason','remarks','created_at'),r)) for r in rows]

