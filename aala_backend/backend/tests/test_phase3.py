from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
from app.modules.auth.service import _token
client.headers.update({'Authorization': f'Bearer {_token("9999999999", "admin", "test-session")}'})

def test_partner_assignment_and_pickup_flow():
    p=client.post('/api/v1/partners',json={'employee_id':'EMP-001','name':'Ravi Kumar','mobile_number':'9999999999','station_code':'ST-01'}); assert p.status_code==200,p.text
    pid=p.json()['partner_id']
    a=client.post(f'/api/v1/partners/{pid}/assign',json={'partner_id':pid,'station_code':'ST-01'}); assert a.status_code==200
    o=client.post('/api/v1/orders',json={'customer_id':'CUS-P3','address_id':'ADDR-P3','service_code':'STANDARD','pickup_slot_id':'MORNING','items':[{'garment_code':'SHIRT','quantity':2}],'payment_method':'UPI'}); assert o.status_code==200
    oid=o.json()['order_id']
    j=client.post(f'/api/v1/pickups/orders/{oid}/assign',json={'partner_id':pid}); assert j.status_code==200
    assert client.post(f'/api/v1/partners/{pid}/orders/{oid}/pickup-start').status_code==200
    assert client.post(f'/api/v1/partners/{pid}/orders/{oid}/arrival',json={'latitude':26.84,'longitude':80.94}).status_code==200
    assert client.post(f'/api/v1/partners/{pid}/orders/{oid}/verify-garments',json={'handover_quantity':2,'customer_confirmed':True}).status_code==200
    assert client.post(f'/api/v1/partners/{pid}/orders/{oid}/damage',json={'item_ref':'SHIRT-1','photo_url':'s3://evidence/1.jpg','description':'pre-existing mark'}).status_code==200
    assert client.post(f'/api/v1/partners/{pid}/orders/{oid}/bag',json={'bag_id':'BAG-001'}).status_code==200
    c=client.post(f'/api/v1/partners/{pid}/orders/{oid}/pickup-complete',json={'received_quantity':2,'customer_confirmed':True}); assert c.status_code==200,c.text
    assert c.json()['order_id']==oid

def test_station_discrepancy_requires_reason():
    o=client.post('/api/v1/orders',json={'customer_id':'CUS-P4','address_id':'ADDR-P4','service_code':'STANDARD','pickup_slot_id':'MORNING','items':[{'garment_code':'SHIRT','quantity':5}],'payment_method':'UPI'}).json()
    oid=o['order_id']
    client.post(f'/api/v1/orders/{oid}/status?new_status=PICKUP')
    client.post(f'/api/v1/orders/{oid}/status?new_status=IRON_STATION')
    r=client.post(f'/api/v1/station/orders/{oid}/receive?station_code=ST-01&partner_id=EMP-001',json={'partner_handover_quantity':5,'station_received_quantity':4})
    assert r.status_code==400
    r=client.post(f'/api/v1/station/orders/{oid}/receive?station_code=ST-01&partner_id=EMP-001',json={'partner_handover_quantity':5,'station_received_quantity':4,'reason':'One garment not in bag','remarks':'Count verified at station'})
    assert r.status_code==200 and r.json()['discrepancy'] is True
