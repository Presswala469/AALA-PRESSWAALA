from copy import deepcopy
from datetime import datetime,timezone
from uuid import uuid4
from app.core.config import settings
from app.core.database import get_connection

_orders={};_events={}
def _id(): return f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"
def create_order(data):
 oid=_id(); now=datetime.now(timezone.utc).isoformat()
 row={**deepcopy(data),'order_id':oid,'status':'BOOKING_CONFIRMED','created_at':now}
 if not settings.database_url:
  _orders[oid]=row;_events[oid]=[{'event_type':'ORDER_CREATED','from_status':None,'to_status':'BOOKING_CONFIRMED','actor':data.get('actor'),'created_at':now}];return deepcopy(row)
 with get_connection() as conn:
  with conn.cursor() as cur:
   cur.execute("""insert into orders(order_id,customer_id,address_id,service_code,pickup_slot_id,status,subtotal,discount,total,currency,payment_method,offer_code,notes)
   values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) returning created_at""",(oid,data['customer_id'],data['address_id'],data['service_code'],data['pickup_slot_id'],'BOOKING_CONFIRMED',data['subtotal'],data['discount'],data['total'],data.get('currency','INR'),data['payment_method'],data.get('offer_code'),data.get('notes')))
   created=cur.fetchone()[0]
   for i in data['items']:
    cur.execute("insert into order_items(order_id,garment_code,quantity,unit_price,line_total) values(%s,%s,%s,%s,%s)",(oid,i['garment_code'],i['quantity'],i['unit_price'],i['line_total']))
   cur.execute("insert into order_events(order_id,event_type,from_status,to_status,actor) values(%s,%s,%s,%s,%s)",(oid,'ORDER_CREATED',None,'BOOKING_CONFIRMED',data.get('actor')))
   conn.commit()
 row['created_at']=created.isoformat() if hasattr(created,'isoformat') else str(created);_orders[oid]=row;return deepcopy(row)
def get_order(oid):
 if not settings.database_url:return deepcopy(_orders.get(oid))
 with get_connection() as conn:
  with conn.cursor() as cur:
   cur.execute("select order_id,customer_id,address_id,service_code,pickup_slot_id,status,currency,subtotal,discount,total,payment_method,created_at from orders where order_id=%s",(oid,));r=cur.fetchone()
   if not r:return None
   cur.execute("select garment_code,quantity,unit_price,line_total from order_items where order_id=%s order by id",(oid,));items=cur.fetchall()
 return dict(zip(('order_id','customer_id','address_id','service_code','pickup_slot_id','status','currency','subtotal','discount','total','payment_method','created_at'),r)) | {'items':[dict(zip(('garment_code','quantity','unit_price','line_total'),x)) for x in items]}
def transition_order(oid,new_status,actor=None,reason=None):
 if not settings.database_url:
  row=_orders.get(oid)
  if not row: return None
  old=row['status'];row['status']=new_status;_events.setdefault(oid,[]).append({'event_type':'STATUS_CHANGED','from_status':old,'to_status':new_status,'actor':actor,'reason':reason,'created_at':datetime.now(timezone.utc).isoformat()});return deepcopy(row)
 with get_connection() as conn:
  with conn.cursor() as cur:
   cur.execute("select status from orders where order_id=%s for update",(oid,));r=cur.fetchone()
   if not r:return None
   old=r[0];cur.execute("update orders set status=%s,updated_at=now() where order_id=%s",(new_status,oid));cur.execute("insert into order_events(order_id,event_type,from_status,to_status,actor,reason) values(%s,%s,%s,%s,%s,%s)",(oid,'STATUS_CHANGED',old,new_status,actor,reason));conn.commit()
 return get_order(oid)
def events(oid):
 if not settings.database_url:return deepcopy(_events.get(oid,[]))
 with get_connection() as conn:
  with conn.cursor() as cur:
   cur.execute("select event_type,from_status,to_status,actor,created_at from order_events where order_id=%s order by created_at",(oid,));rows=cur.fetchall()
 return [dict(zip(('event_type','from_status','to_status','actor','created_at'),r)) for r in rows]

