from app.modules.pricing.service import quote
from app.modules.orders.repository import create_order,get_order,transition_order,events
from app.modules.orders.state_machine import transition
from app.modules.offers.service import apply as apply_offer

def create(data):
 q=quote(data['service_code'],[x for x in data['items']],data.get('station_code'))
 discount=0
 if data.get('offer_code'):
  applied=apply_offer({'code':data['offer_code'],'subtotal':q['subtotal'],'customer_type':data.get('customer_type'),'city':data.get('city'),'station_code':data.get('station_code'),'area':data.get('area'),'building':data.get('building')})
  discount=applied['discount']
 row=create_order({**data,'items':q['items'],'subtotal':q['subtotal'],'discount':discount,'total':q['total']-discount,'currency':q['currency']})
 return row
def get(oid): return get_order(oid)
def change_status(oid,new_status,actor=None,reason=None):
 row=get_order(oid)
 if not row: return None
 transition(row['status'],new_status)
 return transition_order(oid,new_status,actor,reason)
def history(oid): return events(oid)

