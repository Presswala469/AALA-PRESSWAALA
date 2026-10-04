from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_catalog_and_quote():
    services=client.get('/api/v1/services').json()
    assert [x['code'] for x in services][:3] == ['STANDARD','OVERNIGHT_EXPRESS','TWO_HOUR_EXPRESS']
    garments=client.get('/api/v1/garments').json()
    assert any(x['code']=='T_SHIRT' and x['small_garment'] for x in garments)
    q=client.post('/api/v1/pricing/quote',json={'service_code':'STANDARD','items':[{'garment_code':'SHIRT','quantity':2},{'garment_code':'TROUSER','quantity':1}]})
    assert q.status_code==200
    assert q.json()['total']=='50.00'

def test_pickup_slots():
    r=client.get('/api/v1/pickups/slots')
    assert r.status_code==200
    assert len(r.json())>=3

def test_order_lifecycle_and_event_history():
    payload={
      'customer_id':'CUS-TEST-1','address_id':'ADDR-TEST-1','service_code':'STANDARD','pickup_slot_id':'MORNING',
      'items':[{'garment_code':'SHIRT','quantity':2}], 'payment_method':'UPI'
    }
    r=client.post('/api/v1/orders',json=payload)
    assert r.status_code==200, r.text
    order=r.json(); oid=order['order_id']
    assert order['status']=='BOOKING_CONFIRMED' and order['total']=='30.00'
    for status in ['PICKUP','IRON_STATION','RECEIVED','READY_FOR_DELIVERY','OUT_FOR_DELIVERY','DELIVERED']:
        rr=client.post(f'/api/v1/orders/{oid}/status',params={'new_status':status,'actor':'test'})
        assert rr.status_code==200, rr.text
    bad=client.post(f'/api/v1/orders/{oid}/status',params={'new_status':'PICKUP'})
    assert bad.status_code==400
    ev=client.get(f'/api/v1/orders/{oid}/events')
    assert ev.status_code==200
    assert len(ev.json())==7
