from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
import json

from app.core.config import settings
from app.core.database import get_connection

_invoices = {}
_items = {}
_audits = {}


def now():
    return datetime.now(timezone.utc).isoformat()


def _invoice_key(invoice_id):
    return invoice_id


def create(data, items):
    iid = f'INV-{datetime.now().strftime("%Y%m%d")}-{uuid4().hex[:8].upper()}'
    row = {**deepcopy(data), 'invoice_id': iid, 'issued_at': now(), 'updated_at': now()}
    if not settings.database_url:
        # Enforce the same business invariant in the in-memory test repository.
        if any(x.get('order_id') == data['order_id'] and x.get('status') in {'DRAFT','ISSUED','PAID'} for x in _invoices.values()):
            raise ValueError('Active invoice already exists for this order')
        _invoices[iid] = row
        _items[iid] = deepcopy(items)
        _audits.setdefault(iid, []).append({'action': 'INVOICE_CREATED', 'old_values': None, 'new_values': deepcopy(row), 'created_at': now()})
        result = deepcopy(row)
        result['items'] = deepcopy(items)
        result['audit_events'] = deepcopy(_audits[iid])
        return result
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """insert into invoices(
                    invoice_id,order_id,invoice_number,company_snapshot,customer_snapshot,order_snapshot,
                    subtotal,discount,tax_amount,tax_rate,cgst_amount,sgst_amount,igst_amount,tax_type,
                    total,currency,payment_reference,status,issued_at,updated_at
                ) values(%s,%s,%s,%s::jsonb,%s::jsonb,%s::jsonb,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())
                returning issued_at,updated_at""",
                (
                    iid, data['order_id'], data['invoice_number'], json.dumps(data['company_snapshot']),
                    json.dumps(data['customer_snapshot']), json.dumps(data['order_snapshot']), data['subtotal'],
                    data['discount'], data['tax_amount'], data['tax_rate'], data['cgst_amount'],
                    data['sgst_amount'], data['igst_amount'], data['tax_type'], data['total'], data['currency'],
                    data.get('payment_reference'), data.get('status', 'ISSUED')
                )
            )
            issued_at, updated_at = cur.fetchone()
            for item in items:
                cur.execute(
                    """insert into invoice_items(
                        invoice_item_id,invoice_id,garment_code,description,quantity,unit_price,line_discount,
                        taxable_amount,tax_rate,tax_amount,line_total
                    ) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        f'IITEM-{uuid4().hex[:12].upper()}', iid, item.get('garment_code'), item['description'],
                        item['quantity'], item['unit_price'], item.get('line_discount', 0), item['taxable_amount'],
                        item.get('tax_rate', data['tax_rate']), item['tax_amount'], item['line_total']
                    )
                )
            cur.execute(
                "insert into invoice_audit_events(invoice_id,action,new_values) values(%s,%s,%s::jsonb)",
                (iid, 'INVOICE_CREATED', json.dumps(row, default=str))
            )
            conn.commit()
    row['issued_at'] = issued_at.isoformat() if hasattr(issued_at, 'isoformat') else str(issued_at)
    row['updated_at'] = updated_at.isoformat() if hasattr(updated_at, 'isoformat') else str(updated_at)
    return row


def _row(cur):
    keys = (
        'invoice_id','order_id','invoice_number','company_snapshot','customer_snapshot','order_snapshot',
        'subtotal','discount','tax_amount','tax_rate','cgst_amount','sgst_amount','igst_amount','tax_type',
        'total','currency','payment_reference','status','issued_at','updated_at'
    )
    r = cur.fetchone()
    return dict(zip(keys, r)) if r else None


def get(invoice_id):
    if not settings.database_url:
        row = _invoices.get(invoice_id)
        if not row: return None
        result = deepcopy(row)
        result['items'] = deepcopy(_items.get(invoice_id, []))
        result['audit_events'] = deepcopy(_audits.get(invoice_id, []))
        return result
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select invoice_id,order_id,invoice_number,company_snapshot,customer_snapshot,order_snapshot,subtotal,discount,tax_amount,tax_rate,cgst_amount,sgst_amount,igst_amount,tax_type,total,currency,payment_reference,status,issued_at,updated_at from invoices where invoice_id=%s", (invoice_id,))
            result = _row(cur)
            if not result: return None
            cur.execute("select garment_code,description,quantity,unit_price,line_discount,taxable_amount,tax_rate,tax_amount,line_total from invoice_items where invoice_id=%s order by id", (invoice_id,))
            result['items'] = [dict(zip(('garment_code','description','quantity','unit_price','line_discount','taxable_amount','tax_rate','tax_amount','line_total'), x)) for x in cur.fetchall()]
            cur.execute("select action,actor_user_id,old_values,new_values,created_at from invoice_audit_events where invoice_id=%s order by created_at", (invoice_id,))
            result['audit_events'] = [dict(zip(('action','actor_user_id','old_values','new_values','created_at'), x)) for x in cur.fetchall()]
            return result


def by_order(order_id):
    if not settings.database_url:
        return [deepcopy(x) for x in _invoices.values() if x['order_id'] == order_id]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select invoice_id,order_id,invoice_number,company_snapshot,customer_snapshot,order_snapshot,subtotal,discount,tax_amount,tax_rate,cgst_amount,sgst_amount,igst_amount,tax_type,total,currency,payment_reference,status,issued_at,updated_at from invoices where order_id=%s order by issued_at desc", (order_id,))
            return [dict(zip(('invoice_id','order_id','invoice_number','company_snapshot','customer_snapshot','order_snapshot','subtotal','discount','tax_amount','tax_rate','cgst_amount','sgst_amount','igst_amount','tax_type','total','currency','payment_reference','status','issued_at','updated_at'), r)) for r in cur.fetchall()]


def next_invoice_number(prefix, order_id):
    if not settings.database_url:
        return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{order_id.replace('ORD-','')[-8:]}"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select count(*) from invoices where invoice_number like %s", (f'{prefix}-%',))
            seq = (cur.fetchone()[0] or 0) + 1
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{seq:05d}"
