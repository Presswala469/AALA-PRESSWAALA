from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.modules.auth.service import _token
from app.modules.orders import repository as order_repo
from app.modules.delivery import service as delivery
from app.modules.ratings import service as ratings

client=TestClient(app)
client.headers.update({'Authorization': f"Bearer {_token('9000000001','customer','phase15-session')}"})

def make_order(status='READY_FOR_DELIVERY'):
    o=order_repo.create_order({'customer_id':'CUS-P15','address_id':'ADDR-P15','service_code':'STANDARD','pickup_slot_id':'MORNING','items':[{'garment_code':'SHIRT','quantity':2,'unit_price':10,'line_total':20}], 'subtotal':20,'discount':0,'total':20,'currency':'INR','payment_method':'UPI','actor':'test'})
    order_repo._orders[o['order_id']]['status']=status
    return o

def test_delivery_code_has_expiry_and_expires():
    o=make_order(); delivery.assign(o['order_id'],'P15'); r=delivery.start(o['order_id'],'P15')
    assert r['delivery_code']['delivery_code'].isdigit()
    assert r['delivery_code']['expires_at']
    import app.modules.delivery.repository as dr
    dr._codes[o['order_id']]['expires_at']=(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat()
    assert dr.code_matches(o['order_id'],r['delivery_code']['delivery_code']) is False

def test_rating_only_after_delivery():
    o=make_order('READY_FOR_DELIVERY')
    with pytest.raises(ValueError,match='only after delivery'):
        ratings.create(o['order_id'],{'customer_id':'CUS-P15','stars':5})

def test_rating_is_one_per_order():
    o=make_order('DELIVERED')
    ratings.create(o['order_id'],{'customer_id':'CUS-P15','stars':5,'comment':'Good'})
    with pytest.raises(ValueError,match='already exists'):
        ratings.create(o['order_id'],{'customer_id':'CUS-P15','stars':4})

def test_tat_rule_api():
    admin=TestClient(app)
    admin.headers.update({'Authorization':f"Bearer {_token('9000000002','admin','tat-session')}"})
    r=admin.post('/api/v1/orders/tat/rules',json={'service_code':'STANDARD','target_minutes':180,'urgent_threshold_minutes':30})
    assert r.status_code==200 and r.json()['target_minutes']==180
    r=admin.get('/api/v1/orders/tat/rules/STANDARD')
    assert r.status_code==200

def test_station_support_lifecycle():
    admin=TestClient(app)
    admin.headers.update({'Authorization':f"Bearer {_token('9000000003','admin','support-session')}"})
    r=admin.post('/api/v1/station-support',json={'station_code':'ST-01','request_type':'POWER','description':'Power issue','priority':'HIGH'})
    assert r.status_code==200
    rid=r.json()['request_id']
    r=admin.get('/api/v1/station-support/ST-01')
    assert r.status_code==200 and any(x['request_id']==rid for x in r.json())
    r=admin.patch(f'/api/v1/station-support/{rid}',json={'status':'RESOLVED'})
    assert r.status_code==200 and r.json()['status']=='RESOLVED'

def test_reorder_creates_new_order():
    o=make_order('DELIVERED')
    r=order_repo._orders[o['order_id']]
    from app.modules.orders.service import reorder
    new=reorder(o['order_id'],'CUS-P15')
    assert new['order_id'] != o['order_id']
    assert new['customer_id']=='CUS-P15'
