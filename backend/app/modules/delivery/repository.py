from copy import deepcopy
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from uuid import uuid4
from app.core.config import settings
from app.core.database import get_connection

_jobs = {}; _codes = {}; _exceptions = {}; _events = []

def now(): return datetime.now(timezone.utc).isoformat()
def _hash(code): return sha256(code.encode()).hexdigest()

def create_job(data):
    job={**deepcopy(data), 'delivery_job_id': f'DEL-{uuid4().hex[:10].upper()}', 'created_at': now(), 'status':'ASSIGNED'}
    if not settings.database_url:
        _jobs[job['order_id']]=job; return deepcopy(job)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into delivery_jobs(delivery_job_id,order_id,partner_id,status,assigned_at) values(%s,%s,%s,%s,now()) returning created_at",(job['delivery_job_id'],job['order_id'],job['partner_id'],job['status']))
            job['created_at']=cur.fetchone()[0].isoformat(); conn.commit()
    return job

def get_job(order_id):
    if not settings.database_url: return deepcopy(_jobs.get(order_id))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select delivery_job_id,order_id,partner_id,status,assigned_at,created_at from delivery_jobs where order_id=%s order by created_at desc limit 1",(order_id,)); r=cur.fetchone()
    return dict(zip(('delivery_job_id','order_id','partner_id','status','assigned_at','created_at'),r)) if r else None

def save_code(order_id, code):
    row={'order_id':order_id,'delivery_code':code,'active':True,'created_at':now(),'expires_at':(datetime.now(timezone.utc)+timedelta(minutes=settings.delivery_code_ttl_minutes)).isoformat()}
    if not settings.database_url:
        _codes[order_id]=row; return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("update delivery_codes set active=false, invalidated_at=now() where order_id=%s and active=true",(order_id,))
            cur.execute("insert into delivery_codes(order_id,delivery_code_hash,expires_at) values(%s,%s,%s) returning generated_at",(order_id,_hash(code),datetime.now(timezone.utc)+timedelta(minutes=settings.delivery_code_ttl_minutes)))
            row['created_at']=cur.fetchone()[0].isoformat(); conn.commit()
    # Never persist the plaintext code.
    row['delivery_code']=code
    return row

def get_code(order_id):
    if not settings.database_url: return deepcopy(_codes.get(order_id))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select order_id,delivery_code_hash,active,generated_at,used_at,invalidated_at,expires_at from delivery_codes where order_id=%s order by created_at desc limit 1",(order_id,)); r=cur.fetchone()
    if not r: return None
    return {'order_id':r[0],'delivery_code_hash':r[1],'active':r[2],'created_at':r[3],'used_at':r[4],'invalidated_at':r[5],'expires_at':r[6]}

def code_matches(order_id, code):
    row=get_code(order_id)
    if not row or not row.get('active') or row.get('delivery_code_hash') == '':
        if not settings.database_url:
            return False
        return False
    expiry=row.get('expires_at')
    if expiry:
        if isinstance(expiry,str):
            expiry=datetime.fromisoformat(expiry.replace('Z','+00:00'))
        if expiry <= datetime.now(timezone.utc):
            if not settings.database_url:
                _codes[order_id]['active']=False
                _codes[order_id]['invalidated_at']=now()
                return False
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('update delivery_codes set active=false, invalidated_at=now() where order_id=%s and active=true',(order_id,))
                conn.commit()
            return False
    if not settings.database_url:
        stored=row.get('delivery_code')
        return bool(stored and stored == code)
    return row['delivery_code_hash']==_hash(code)

def invalidate_code(order_id):
    if not settings.database_url:
        if order_id in _codes: _codes[order_id]['active']=False; _codes[order_id]['invalidated_at']=now()
        return get_code(order_id)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("update delivery_codes set active=false, used_at=now(), invalidated_at=now() where order_id=%s and active=true",(order_id,)); conn.commit()
    return get_code(order_id)

def save_event(order_id,data):
    row={'order_id':order_id,**deepcopy(data),'created_at':now()}
    if not settings.database_url:
        _events.append(row); return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""insert into delivery_events(order_id,partner_id,delivery_mode,receiver_name,receiver_mobile,latitude,longitude,evidence_url,house_number,reason,remarks,delivered_at)
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now()) returning delivered_at,created_at""",
                (order_id,data['partner_id'],data['delivery_mode'],data.get('receiver_name'),data.get('receiver_mobile'),data.get('latitude'),data.get('longitude'),data.get('evidence_url'),data.get('house_number'),data.get('reason'),data.get('remarks')))
            delivered,created=cur.fetchone(); row['delivered_at']=delivered; row['created_at']=created; conn.commit()
    return row

def save_exception(order_id,data): return save_event(order_id,{'delivery_mode':'MANUAL','reason':data.get('reason'),**data})
def list_exceptions(order_id):
    if not settings.database_url:return deepcopy([x for x in _events if x.get('order_id')==order_id and x.get('delivery_mode')=='MANUAL'])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select order_id,partner_id,delivery_mode,receiver_name,receiver_mobile,latitude,longitude,evidence_url,house_number,reason,remarks,delivered_at,created_at from delivery_events where order_id=%s and delivery_mode='MANUAL' order by created_at desc",(order_id,)); rows=cur.fetchall()
    keys=('order_id','partner_id','delivery_mode','receiver_name','receiver_mobile','latitude','longitude','evidence_url','house_number','reason','remarks','delivered_at','created_at')
    return [dict(zip(keys,r)) for r in rows]
