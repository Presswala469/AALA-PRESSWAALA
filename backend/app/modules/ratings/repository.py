from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
from app.core.config import settings
from app.core.database import get_connection

_ratings = {}

def now(): return datetime.now(timezone.utc).isoformat()

def create(order_id, data):
    if order_id in _ratings:
        raise ValueError('Rating already exists for this order')
    row={**deepcopy(data),'order_id':order_id,'created_at':now()}
    if not settings.database_url:
        _ratings[order_id]=row
        return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select 1 from order_ratings where order_id=%s',(order_id,))
            if cur.fetchone(): raise ValueError('Rating already exists for this order')
            cur.execute('''insert into order_ratings(order_id,customer_id,stars,comment) values(%s,%s,%s,%s) returning created_at''',
                        (order_id,data['customer_id'],data['stars'],data.get('comment')))
            row['created_at']=cur.fetchone()[0].isoformat(); conn.commit()
    return row

def get(order_id):
    if not settings.database_url: return deepcopy(_ratings.get(order_id))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select order_id,customer_id,stars,comment,created_at from order_ratings where order_id=%s',(order_id,)); r=cur.fetchone()
    return dict(zip(('order_id','customer_id','stars','comment','created_at'),r)) if r else None
