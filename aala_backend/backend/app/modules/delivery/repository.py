from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
from app.core.config import settings
from app.core.database import get_connection

_jobs={}; _codes={}; _exceptions={}
def now(): return datetime.now(timezone.utc).isoformat()
def create_job(data):
    job={**deepcopy(data), 'delivery_job_id': f'DEL-{uuid4().hex[:10].upper()}', 'created_at': now(), 'status':'ASSIGNED'}
    if not settings.database_url: _jobs[job['order_id']]=job; return deepcopy(job)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into delivery_jobs(delivery_job_id,order_id,partner_id,status,assigned_at) values(%s,%s,%s,%s,now())",(job['delivery_job_id'],job['order_id'],job['partner_id'],job['status'])); conn.commit()
    return job
def get_job(order_id):
    if not settings.database_url: return deepcopy(_jobs.get(order_id))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select delivery_job_id,order_id,partner_id,status,assigned_at,created_at from delivery_jobs where order_id=%s order by created_at desc limit 1",(order_id,)); r=cur.fetchone()
    return dict(zip(('delivery_job_id','order_id','partner_id','status','assigned_at','created_at'),r)) if r else None
def save_code(order_id, code):
    row={'order_id':order_id,'delivery_code':code,'active':True,'created_at':now()}; _codes[order_id]=row; return deepcopy(row)
def get_code(order_id): return deepcopy(_codes.get(order_id))
def invalidate_code(order_id):
    if order_id in _codes: _codes[order_id]['active']=False; _codes[order_id]['invalidated_at']=now()
    return get_code(order_id)
def save_exception(order_id,data): _exceptions.setdefault(order_id,[]).append({**deepcopy(data),'created_at':now()}); return deepcopy(_exceptions[order_id][-1])
def list_exceptions(order_id): return deepcopy(_exceptions.get(order_id,[]))

