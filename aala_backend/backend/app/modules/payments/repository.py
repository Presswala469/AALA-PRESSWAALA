from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
from app.core.config import settings
from app.core.database import get_connection
_payments={}; _transactions={}; _events={}
def now(): return datetime.now(timezone.utc).isoformat()
def create_payment(data):
    pid=f'PAY-{uuid4().hex[:10].upper()}'; row={**deepcopy(data),'payment_id':pid,'status':data.get('status','CREATED'),'created_at':now()}
    if not settings.database_url: _payments[pid]=row; return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into payments(payment_id,order_id,method,amount,currency,status,provider) values(%s,%s,%s,%s,%s,%s,%s)",(pid,data['order_id'],data['method'],data['amount'],data['currency'],data.get('status','CREATED'),data.get('provider','mock'))); conn.commit()
    return row
def update_payment(payment_id, status, **values):
    row=_payments.get(payment_id)
    if row: row.update(values,status=status,updated_at=now()); return deepcopy(row)
    if not settings.database_url:return None
    sets=', '.join(f'{k}=%s' for k in values)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"update payments set status=%s,{sets},updated_at=now() where payment_id=%s",(status,*values.values(),payment_id)); conn.commit()
            cur.execute("select payment_id,order_id,method,amount,currency,status,provider,provider_order_id,provider_payment_id from payments where payment_id=%s",(payment_id,)); r=cur.fetchone()
    return dict(zip(('payment_id','order_id','method','amount','currency','status','provider','provider_order_id','provider_payment_id'),r)) if r else None
def get(payment_id):
    if not settings.database_url:return deepcopy(_payments.get(payment_id))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select payment_id,order_id,method,amount,currency,status,provider,provider_order_id,provider_payment_id from payments where payment_id=%s",(payment_id,)); r=cur.fetchone()
    return dict(zip(('payment_id','order_id','method','amount','currency','status','provider','provider_order_id','provider_payment_id'),r)) if r else None
def list_for_order(order_id):
    if not settings.database_url:
        return [deepcopy(x) for x in _payments.values() if x["order_id"] == order_id]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select payment_id,order_id,method,amount,currency,status,provider,provider_order_id,provider_payment_id from payments where order_id=%s order by payment_id desc",(order_id,))
            rows=cur.fetchall()
    keys=("payment_id","order_id","method","amount","currency","status","provider","provider_order_id","provider_payment_id")
    return [dict(zip(keys,r)) for r in rows]
def event(payment_id,event_type,data): _events.setdefault(payment_id,[]).append({'event_type':event_type,**deepcopy(data),'created_at':now()}); return deepcopy(_events[payment_id][-1])

