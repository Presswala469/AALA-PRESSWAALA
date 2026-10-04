import pytest
from app.modules.orders import repository as order_repo
from app.modules.station_operations import service

@pytest.fixture(autouse=True)
def reset():
    order_repo._orders.clear(); order_repo._events.clear()

def make_order(status='IRON_STATION'):
    return order_repo.create_order({'customer_id':'C1','address_id':'A1','service_code':'STANDARD','pickup_slot_id':'S1','items':[{'garment_code':'SHIRT','quantity':2,'unit_price':10,'line_total':20}], 'subtotal':20,'discount':0,'total':20,'currency':'INR','payment_method':'COD','actor':'test'})

def test_receive_moves_order_to_received():
    o=make_order(); order_repo._orders[o['order_id']]['status']='IRON_STATION'
    r=service.receive(o['order_id'],'ST01','P01',{'partner_handover_quantity':2,'station_received_quantity':2})
    assert r['order']['status']=='RECEIVED'

def test_discrepancy_requires_reason():
    o=make_order(); order_repo._orders[o['order_id']]['status']='IRON_STATION'
    with pytest.raises(ValueError,match='Reason is required'):
        service.receive(o['order_id'],'ST01','P01',{'partner_handover_quantity':2,'station_received_quantity':1})

def test_discrepancy_is_recorded():
    o=make_order(); order_repo._orders[o['order_id']]['status']='IRON_STATION'
    r=service.receive(o['order_id'],'ST01','P01',{'partner_handover_quantity':2,'station_received_quantity':1,'reason':'Missing garment'})
    assert r['discrepancy'] is True and r['order']['status']=='RECEIVED'

def test_ready_for_delivery_transition():
    o=make_order(); order_repo._orders[o['order_id']]['status']='RECEIVED'
    r=service.status(o['order_id'],'ST01',{'status':'READY_FOR_DELIVERY'})
    assert r['order']['status']=='READY_FOR_DELIVERY'

def test_invalid_station_status_rejected():
    o=make_order()
    with pytest.raises(ValueError,match='Invalid station status'):
        service.status(o['order_id'],'ST01',{'status':'IRONING_STARTED'})
