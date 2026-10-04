from copy import deepcopy
from datetime import datetime, timezone
from app.core.config import settings
from app.modules.reports import repository
from app.modules.reports.schemas import aREPORT_TYPES

REPORT_TYPES = aREPORT_TYPES

def _in_range(value, f):
    if not value: return True
    try: dt=datetime.fromisoformat(str(value).replace('Z','+00:00'))
    except ValueError: return True
    if f.get('date_from') and dt.date() < f['date_from']: return False
    if f.get('date_to') and dt.date() > f['date_to']: return False
    return True

def _memory_report(report_type, f):
    from app.modules.orders import repository as orders
    from app.modules.customers import repository as customers
    from app.modules.partners import repository as partners
    from app.modules.inventory import repository as inventory
    from app.modules.hangers import repository as hangers
    from app.modules.complaints import repository as complaints
    rows=[]
    if report_type == 'orders':
        for row in orders._orders.values():
            if not _in_range(row.get('created_at'), f): continue
            if f.get('customer_id') and row.get('customer_id') != f['customer_id']: continue
            if f.get('status') and row.get('status') != f['status']: continue
            if f.get('service_code') and row.get('service_code') != f['service_code']: continue
            rows.append({k: deepcopy(row.get(k)) for k in ('order_id','customer_id','address_id','service_code','pickup_slot_id','status','subtotal','discount','total','payment_method','offer_code','created_at')})
        return sorted(rows,key=lambda x:str(x.get('created_at')),reverse=True)[:f.get('limit',500)]
    if report_type == 'revenue':
        orders_rows=_memory_report('orders',f)
        return [{
            'order_count':len(orders_rows),
            'gross_subtotal':sum(float(x.get('subtotal',0) or 0) for x in orders_rows),
            'discounts':sum(float(x.get('discount',0) or 0) for x in orders_rows),
            'net_revenue':sum(float(x.get('total',0) or 0) for x in orders_rows),
            'cod_value':sum(float(x.get('total',0) or 0) for x in orders_rows if x.get('payment_method')=='COD'),
            'prepaid_value':sum(float(x.get('total',0) or 0) for x in orders_rows if x.get('payment_method')!='COD'),
        }]
    if report_type == 'customers':
        for row in customers._customers.values():
            if f.get('customer_id') and row.get('customer_id') != f['customer_id']: continue
            order_rows=[o for o in orders._orders.values() if o.get('customer_id')==row.get('customer_id')]
            rows.append({**{k:deepcopy(row.get(k)) for k in ('customer_id','global_customer_number','name','mobile_number','email')},'status':'active' if row.get('is_active',True) else 'inactive','created_at':row.get('created_at'),'order_count':len(order_rows),'lifetime_value':sum(float(o.get('total',0) or 0) for o in order_rows)})
        return rows[:f.get('limit',500)]
    if report_type == 'partners':
        for row in partners._partners.values(): rows.append({k:deepcopy(row.get(k)) for k in ('partner_id','employee_id','name','mobile_number','active','created_at')})
        return rows[:f.get('limit',500)]
    if report_type == 'bags_boxes':
        grouped={}
        for row in inventory._items.values():
            if f.get('item_type') and row.get('item_type') != f['item_type']: continue
            if f.get('status') and row.get('status') != f['status']: continue
            key=(row.get('item_type'),row.get('status')); grouped[key]=grouped.get(key,0)+1
        return [{'item_type':k[0],'status':k[1],'quantity':v} for k,v in grouped.items()]
    if report_type == 'hangers':
        grouped={}
        for row in hangers._hangers.values(): grouped[row.get('status')]=grouped.get(row.get('status'),0)+int(row.get('quantity',0) or 0)
        return [{'status':k,'quantity':v,'record_count':sum(1 for x in hangers._hangers.values() if x.get('status')==k)} for k,v in grouped.items()]
    if report_type == 'complaints':
        for row in complaints._complaints.values():
            if f.get('status') and row.get('status') != f['status']: continue
            if f.get('category') and row.get('category') != f['category']: continue
            rows.append(deepcopy(row))
        return rows[:f.get('limit',500)]
    if report_type in {'garments','stations','offers','customer_locations','customer_history'}:
        return []
    raise ValueError('Unsupported report type')

def generate(report_type, filters):
    if report_type not in REPORT_TYPES: raise ValueError('Unsupported report type')
    return repository.report(report_type, filters)

