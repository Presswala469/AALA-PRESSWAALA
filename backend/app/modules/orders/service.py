from app.modules.pricing.service import quote
from app.modules.orders.repository import create_order,get_order,transition_order,events
from app.modules.orders.state_machine import transition
from app.modules.offers.service import apply as apply_offer
from app.modules.orders.tat import calculate_due

def create(data):
 q=quote(data['service_code'],[x for x in data['items']],data.get('station_code'))
 discount=0
 if data.get('offer_code'):
  applied=apply_offer({'code':data['offer_code'],'subtotal':q['subtotal'],'customer_type':data.get('customer_type'),'city':data.get('city'),'station_code':data.get('station_code'),'area':data.get('area'),'building':data.get('building')})
  discount=applied['discount']
 
 # Build immutable booking/customer/address snapshots when the records are available.
 customer_snapshot={'customer_id':data.get('customer_id')}
 address_snapshot={'address_id':data.get('address_id')}
 try:
  from app.modules.customers.service import get as get_customer
  c=get_customer(data['customer_id'])
  if c: customer_snapshot={k:c.get(k) for k in ('customer_id','global_customer_number','name','mobile_number','email')}
 except Exception: pass
 try:
  from app.modules.addresses.service import list_current_and_history
  rows=list_current_and_history(data['customer_id'])
  for a in rows:
   if a.get('address_id')==data.get('address_id') or a.get('is_current'):
    address_snapshot=dict(a); break
 except Exception: pass
 started=data.get('tat_started_at')
 due=calculate_due(data['service_code'],started)
 row=create_order({**data,'items':q['items'],'subtotal':q['subtotal'],'discount':discount,'total':q['total']-discount,'currency':q['currency'],'customer_snapshot':customer_snapshot,'address_snapshot':address_snapshot,'booking_snapshot':{'service_code':data['service_code'],'pickup_slot_id':data['pickup_slot_id'],'offer_code':data.get('offer_code'),'payment_method':data['payment_method']},'tat_started_at':started,'tat_due_at':due.isoformat() if due else data.get('tat_due_at')})
 return row
def get(oid): return get_order(oid)
def change_status(oid,new_status,actor=None,reason=None):
 row=get_order(oid)
 if not row: return None
 transition(row['status'],new_status)
 return transition_order(oid,new_status,actor,reason)
def history(oid): return events(oid)



def reorder(order_id, customer_id):
    previous=get_order(order_id)
    if not previous: raise ValueError('Order not found')
    if previous['customer_id'] != customer_id: raise ValueError('Customer access denied')
    payload={'customer_id':customer_id,'address_id':previous['address_id'],'service_code':previous['service_code'],'pickup_slot_id':previous['pickup_slot_id'],'items':[{'garment_code':x['garment_code'],'quantity':x['quantity']} for x in previous.get('items',[])],'payment_method':previous['payment_method']}
    return create(payload)
