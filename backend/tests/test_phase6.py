import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from app.modules.orders import repository as order_repo
from app.modules.orders import service as order_service
from app.modules.offers import repository as offer_repo
from app.modules.offers import service as offer_service
from app.modules.complaints import repository as complaint_repo
from app.modules.complaints import service as complaint_service
from app.modules.notifications import service as notification_service, repository as notification_repo
from app.modules.hangers import service as hanger_service, repository as hanger_repo

@pytest.fixture(autouse=True)
def reset():
    order_repo._orders.clear(); order_repo._events.clear(); offer_repo._offers.clear(); offer_repo._usage.clear()
    complaint_repo._complaints.clear(); complaint_repo._events.clear(); notification_repo._notifications.clear(); notification_repo._devices.clear(); notification_repo._preferences.clear(); notification_repo._attempts.clear()
    hanger_repo._hangers.clear(); hanger_repo._returns.clear(); hanger_repo._movements.clear()

def make_order(status='BOOKING_CONFIRMED'):
    o=order_repo.create_order({'customer_id':'C1','address_id':'A1','service_code':'STANDARD','pickup_slot_id':'S1','items':[{'garment_code':'SHIRT','quantity':2,'unit_price':10,'line_total':20}], 'subtotal':20,'discount':0,'total':20,'currency':'INR','payment_method':'UPI','actor':'test'})
    order_repo._orders[o['order_id']]['status']=status
    if status=='DELIVERED': order_repo._events[o['order_id']].append({'event_type':'STATUS_CHANGED','from_status':'OUT_FOR_DELIVERY','to_status':'DELIVERED','created_at':datetime.now(timezone.utc).isoformat()})
    return o

def test_percent_offer_with_cap():
    offer_service.create({'code':'SAVE20','name':'Save 20','discount_type':'PERCENT','discount_value':20,'min_order':50,'max_discount':100,'priority':1,'enabled':True})
    result=offer_service.apply({'code':'SAVE20','subtotal':Decimal('600')})
    assert result['discount']==Decimal('100') and result['payable']==Decimal('500')

def test_offer_is_used_by_order_creation():
    offer_service.create({'code':'SAVE10','name':'Save 10','discount_type':'PERCENT','discount_value':10,'min_order':0,'priority':1,'enabled':True})
    o=order_service.create({'customer_id':'C1','address_id':'A1','service_code':'STANDARD','pickup_slot_id':'S1','items':[{'garment_code':'SHIRT','quantity':2}], 'payment_method':'UPI','offer_code':'SAVE10'})
    assert Decimal(str(o['discount']))==Decimal('3') and Decimal(str(o['total']))==Decimal('27')

def test_complaint_window_and_status_lifecycle():
    o=make_order('DELIVERED')
    c=complaint_service.create({'order_id':o['order_id'],'customer_id':'C1','category':'DAMAGE','description':'Visible damage','evidence_urls':['s3://x']})
    assert c['status']=='NEW'
    c2=complaint_service.update(c['complaint_id'],{'status':'ASSIGNED','remarks':'Assigned','assigned_to':'A1'})
    assert c2['status']=='ASSIGNED'
    c3=complaint_service.update(c['complaint_id'],{'status':'UNDER_INVESTIGATION','remarks':'Checking'})
    assert c3['status']=='UNDER_INVESTIGATION'

def test_complaint_expired_after_24h():
    o=make_order('DELIVERED'); order_repo._events[o['order_id']][-1]['created_at']=(datetime.now(timezone.utc)-timedelta(hours=25)).isoformat()
    with pytest.raises(ValueError,match='24 hours'):
        complaint_service.create({'order_id':o['order_id'],'customer_id':'C1','category':'OTHER','description':'Late complaint'})

def test_notification_queue_and_status():
    n=notification_service.queue({'recipient_id':'C1','channel':'IN_APP','title':'Booking','message':'Confirmed'})
    assert n['status']=='QUEUED'
    assert notification_service.mark(n['notification_id'],'SENT')['status']=='SENT'

def test_hanger_issue_and_return_request():
    h=hanger_service.create({'customer_id':'C1','order_id':'O1','quantity':2})
    assert h['status']=='ISSUED'
    assert hanger_service.update(h['hanger_id'],{'status':'RETURNED'})['status']=='RETURNED'
    r=hanger_service.request_return({'customer_id':'C1','address_id':'A1','quantity':2,'preferred_slot_id':'S1'})
    assert r['status']=='REQUESTED'

def test_notification_idempotency_in_memory():
    a=notification_service.queue({'recipient_id':'C1','channel':'IN_APP','title':'A','message':'B','idempotency_key':'ORDER-O1-READY'})
    b=notification_service.queue({'recipient_id':'C1','channel':'IN_APP','title':'A2','message':'B2','idempotency_key':'ORDER-O1-READY'})
    assert a['notification_id']==b['notification_id']

def test_notification_device_registration_and_deactivation():
    d=notification_service.register_device({'user_id':'C1','platform':'ANDROID','token':'token-1234567890'})
    assert d['active'] is True
    assert notification_repo.deactivate_device('token-1234567890') is True
    assert notification_repo.active_tokens('C1')==[]


def test_notification_event_dispatch_respects_preferences():
    notification_service.set_preference({"user_id":"C1","event_type":"BOOKING","channel":"PUSH","enabled":False})
    out=notification_service.dispatch_event({
        "recipient_id":"C1","event_type":"BOOKING","title":"Booking","message":"Confirmed",
        "idempotency_key":"BOOKING-O1"
    })
    assert len(out)==1
    assert out[0]["channel"]=="IN_APP"
    assert out[0]["idempotency_key"]=="BOOKING-O1:IN_APP"

def test_notification_read_and_recipient_isolation_in_service():
    n=notification_service.queue({"recipient_id":"C1","channel":"IN_APP","title":"A","message":"B"})
    assert notification_service.mark(n["notification_id"],"READ")["status"]=="READ"

def test_device_re_registration_updates_single_token():
    a=notification_service.register_device({"user_id":"C1","platform":"ANDROID","token":"token-abcdefghij","app_version":"1.0"})
    b=notification_service.register_device({"user_id":"C1","platform":"ANDROID","token":"token-abcdefghij","app_version":"1.1"})
    assert b["active"] is True
    assert b["app_version"]=="1.1"
    assert notification_repo.active_tokens("C1")==["token-abcdefghij"]

def test_notification_send_without_provider_fails_audibly():
    n=notification_service.queue({"recipient_id":"C1","channel":"PUSH","title":"A","message":"B"})
    notification_service.register_device({"user_id":"C1","platform":"ANDROID","token":"token-abcdefghij"})
    result=notification_service.send(n["notification_id"])
    assert result["status"]=="FAILED"
    assert result["failure_code"]=="PROVIDER_NOT_CONFIGURED"
    assert len(notification_repo._attempts)==1
