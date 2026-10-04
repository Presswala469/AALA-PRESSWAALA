from datetime import datetime, timezone
from uuid import uuid4
from copy import deepcopy
from app.core.config import settings
from app.core.database import get_connection
credits={}; refunds={}
def now(): return datetime.now(timezone.utc).isoformat()
def create_credit(d,actor):
    cid=f'CR-{uuid4().hex[:10].upper()}'; row={**d,'credit_id':cid,'status':'ISSUED','issued_by':actor,'created_at':now()}
    if settings.database_url:
        with get_connection() as c:
            with c.cursor() as x:x.execute('insert into service_credits(credit_id,customer_id,order_id,amount,reason,status,issued_by) values(%s,%s,%s,%s,%s,%s,%s)',(cid,d['customer_id'],d.get('order_id'),d['amount'],d['reason'],'ISSUED',actor));c.commit()
    credits[cid]=row; return deepcopy(row)
def list_credits(customer_id=None):
    if settings.database_url:
        with get_connection() as c:
            with c.cursor() as x:
                q='select credit_id,customer_id,order_id,amount,reason,status,issued_by,created_at from service_credits';p=[]
                if customer_id:q+=' where customer_id=%s';p=[customer_id]
                q+=' order by created_at desc';x.execute(q,p);rows=x.fetchall();return [dict(zip(('credit_id','customer_id','order_id','amount','reason','status','issued_by','created_at'),r)) for r in rows]
    return [deepcopy(v) for v in credits.values() if not customer_id or v['customer_id']==customer_id]
def create_refund(d,actor):
    rid=f'RF-{uuid4().hex[:10].upper()}';row={**d,'refund_id':rid,'status':'PENDING','requested_by':actor,'created_at':now(),'updated_at':now()}
    if settings.database_url:
        with get_connection() as c:
            with c.cursor() as x:x.execute('insert into refund_requests(refund_id,order_id,payment_id,amount,reason,status,requested_by) values(%s,%s,%s,%s,%s,%s,%s)',(rid,d['order_id'],d.get('payment_id'),d['amount'],d['reason'],'PENDING',actor));c.commit()
    refunds[rid]=row;return deepcopy(row)
def update_refund(rid,d,actor):
    row=refunds.get(rid)
    if not row and settings.database_url:
        with get_connection() as c:
            with c.cursor() as x:x.execute('select refund_id,order_id,payment_id,amount,reason,status,requested_by,created_at from refund_requests where refund_id=%s',(rid,));r=x.fetchone()
        if r: row=dict(zip(('refund_id','order_id','payment_id','amount','reason','status','requested_by','created_at'),r))
    if not row:return None
    row.update(d,updated_by=actor,updated_at=now());refunds[rid]=row
    if settings.database_url:
        with get_connection() as c:
            with c.cursor() as x:x.execute('update refund_requests set status=%s,remarks=%s,processed_by=%s,processed_at=case when %s in (\'PROCESSED\',\'REJECTED\') then now() else processed_at end,updated_at=now() where refund_id=%s',(d['status'],d.get('remarks'),actor,d['status'],rid));c.commit()
    return deepcopy(row)
def get_refund(rid): return deepcopy(refunds.get(rid))
