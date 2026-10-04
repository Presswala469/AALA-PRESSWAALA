from app.modules.pricing.service import quote
from app.modules.orders.repository import create_order,get_order,transition_order,events
from app.modules.orders.state_machine import transition

from app.modules.offers.service import apply as apply_offer

def _notify(recipient_id, event_type, title, message, order_id, actor_user_id=None):
    # Notifications must never break the transactional order workflow.
    try:
        from app.modules.notifications.service import dispatch_event
        dispatch_event({
            "recipient_id": str(recipient_id),
            "event_type": event_type,
            "title": title,
            "message": message,
            "data": {"order_id": str(order_id)},
            "idempotency_key": f"ORDER:{order_id}:{event_type}",
        }, actor_user_id=actor_user_id)
    except Exception:
        pass

def create(data):
    q=quote(data['service_code'],[x for x in data['items']],data.get('station_code'))
    discount=0
    if data.get('offer_code'):
        applied=apply_offer({'code':data['offer_code'],'subtotal':q['subtotal'],'customer_type':data.get('customer_type'),'city':data.get('city'),'station_code':data.get('station_code'),'area':data.get('area'),'building':data.get('building')})
        discount=applied['discount']
    row=create_order({**data,'items':q['items'],'subtotal':q['subtotal'],'discount':discount,'total':q['total']-discount,'currency':q['currency']})
    _notify(row.get("customer_id"),"BOOKING","Booking Confirmed",
            f"Your booking {row['order_id']} has been confirmed.",row["order_id"])
    return row

def get(oid): return get_order(oid)

def change_status(oid,new_status,actor=None,reason=None):
    row=get_order(oid)
    if not row: return None
    transition(row['status'],new_status)
    changed=transition_order(oid,new_status,actor,reason)
    event_map={
        "PICKUP_ASSIGNED":"ASSIGNMENT",
        "PICKED_UP":"ARRIVAL_PICKUP",
        "STATION_RECEIVED":"STATION_RECEIPT",
        "READY_FOR_DELIVERY":"READY",
        "OUT_FOR_DELIVERY":"OUT_FOR_DELIVERY",
        "DELIVERED":"DELIVERED",
        "CANCELLED":"STATUS",
    }
    event_type=event_map.get(new_status,"STATUS")
    _notify(changed.get("customer_id"),event_type,f"Order {new_status.replace('_',' ').title()}",
            f"Your order {oid} is now {new_status.replace('_',' ').title()}.",oid)
    return changed

def history(oid): return events(oid)
