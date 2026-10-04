import pytest
from app.modules.orders import repository as order_repo
from app.modules.delivery import service as delivery
from app.modules.hangers import service as hangers

@pytest.fixture(autouse=True)
def reset():
    order_repo._orders.clear(); order_repo._events.clear()
    import app.modules.delivery.repository as dr
    dr._jobs.clear(); dr._codes.clear(); dr._exceptions.clear(); dr._events.clear()
    import app.modules.hangers.repository as hr
    hr._hangers.clear(); hr._returns.clear(); hr._movements.clear()

def make_order(status='READY_FOR_DELIVERY'):
    o=order_repo.create_order({'customer_id':'C1','address_id':'A1','service_code':'STANDARD','pickup_slot_id':'S1','items':[{'garment_code':'SHIRT','quantity':2,'unit_price':10,'line_total':20}], 'subtotal':20,'discount':0,'total':20,'currency':'INR','payment_method':'UPI','actor':'test'})
    order_repo._orders[o['order_id']]['status']=status
    return o

def test_code_is_not_exposed_from_persistent_style_record():
    o=make_order(); delivery.assign(o['order_id'],'P01'); r=delivery.start(o['order_id'],'P01')
    assert r['delivery_code']['delivery_code'].isdigit()
    stored=delivery.get_code(o['order_id'])
    assert 'delivery_code_hash' not in stored

def test_standard_delivery_requires_gps():
    o=make_order(); delivery.assign(o['order_id'],'P01'); r=delivery.start(o['order_id'],'P01')
    with pytest.raises(Exception):
        from app.modules.delivery.schemas import DeliveryConfirm
        DeliveryConfirm(delivery_code=r['delivery_code']['delivery_code'],receiver_name='R')

def test_manual_delivery_requires_evidence_receiver_and_gps():
    o=make_order(); delivery.assign(o['order_id'],'P01'); delivery.start(o['order_id'],'P01')
    with pytest.raises(Exception):
        from app.modules.delivery.schemas import DeliveryException
        DeliveryException(reason='phone issue',receiver_name='R',receiver_mobile='9999999999',latitude=26,longitude=80)

def test_manual_delivery_completes_with_evidence():
    o=make_order(); delivery.assign(o['order_id'],'P01'); delivery.start(o['order_id'],'P01')
    r=delivery.exception(o['order_id'],'P01',{'reason':'phone issue','receiver_name':'R','receiver_mobile':'9999999999','evidence_url':'s3://evidence/x.jpg','latitude':26.8,'longitude':80.9,'remarks':'verified'})
    assert r['order']['status']=='DELIVERED' and r['event']['delivery_mode']=='MANUAL'

def test_hanger_pending_red_alert_after_30_days():
    from datetime import datetime, timedelta, timezone
    o=hangers.create({'customer_id':'C1','order_id':'O1','quantity':1,'status':'PENDING'})
    import app.modules.hangers.repository as hr
    hr._hangers[o['hanger_id']]['updated_at']=(datetime.now(timezone.utc)-timedelta(days=31)).isoformat()
    hr._hangers[o['hanger_id']]['pending_since']=(datetime.now(timezone.utc)-timedelta(days=31)).isoformat()
    r=hangers.get(o['hanger_id'])
    assert r['alert_level']=='RED' and r['pending_days']>30
