from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
from app.core.config import settings
from app.core.database import get_connection
_invoices={}
def now(): return datetime.now(timezone.utc).isoformat()
def create(data):
    iid=f'INV-{datetime.now().strftime("%Y%m%d")}-{uuid4().hex[:8].upper()}'
    row={**deepcopy(data),'invoice_id':iid,'issued_at':now()}
    if not settings.database_url: _invoices[iid]=row; return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into invoices(invoice_id,order_id,invoice_number,company_snapshot,subtotal,discount,tax_amount,total,currency,issued_at) values(%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,now())",(iid,data['order_id'],data['invoice_number'],__import__('json').dumps(data['company_snapshot']),data['subtotal'],data['discount'],data['tax_amount'],data['total'],data['currency'])); conn.commit()
    return row
def get(invoice_id):
    if not settings.database_url:return deepcopy(_invoices.get(invoice_id))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select invoice_id,order_id,invoice_number,company_snapshot,subtotal,discount,tax_amount,total,currency,issued_at from invoices where invoice_id=%s",(invoice_id,)); r=cur.fetchone()
    if not r:return None
    return dict(zip(('invoice_id','order_id','invoice_number','company_snapshot','subtotal','discount','tax_amount','total','currency','issued_at'),r))
def by_order(order_id):
    if not settings.database_url:return [deepcopy(x) for x in _invoices.values() if x['order_id']==order_id]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select invoice_id,order_id,invoice_number,company_snapshot,subtotal,discount,tax_amount,total,currency,issued_at from invoices where order_id=%s order by issued_at desc",(order_id,)); rows=cur.fetchall()
    return [dict(zip(('invoice_id','order_id','invoice_number','company_snapshot','subtotal','discount','tax_amount','total','currency','issued_at'),r)) for r in rows]

