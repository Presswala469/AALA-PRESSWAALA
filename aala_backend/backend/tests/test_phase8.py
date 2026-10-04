import pytest
from app.modules.reports import service as reports_service
from app.modules.orders import repository as orders_repo
from app.modules.customers import repository as customers_repo
from app.modules.inventory import repository as inventory_repo
from app.modules.hangers import repository as hangers_repo

@pytest.fixture(autouse=True)
def reset():
    orders_repo._orders.clear(); orders_repo._events.clear()
    customers_repo._customers.clear(); inventory_repo._items.clear(); inventory_repo._movements.clear()
    hangers_repo._hangers.clear(); hangers_repo._returns.clear(); hangers_repo._movements.clear()

def test_report_type_catalog_is_complete():
    expected={'revenue','orders','customers','partners','stations','garments','hangers','bags_boxes','offers','complaints','customer_locations','customer_history'}
    assert expected.issubset(reports_service.REPORT_TYPES)

def reset_phase8():
    from app.modules.orders import repository as orp
    from app.modules.inventory import repository as irp
    from app.modules.hangers import repository as hrp
    orp._orders.clear(); orp._events.clear()
    irp._items.clear(); irp._movements.clear()
    hrp._hangers.clear(); hrp._returns.clear(); hrp._movements.clear()

@pytest.fixture(autouse=True)
def _reset_phase8():
    reset_phase8()
    yield

def test_orders_and_revenue_reports_use_same_operational_data():
    orders_repo.create_order({'customer_id':'C1','address_id':'A1','service_code':'STANDARD','pickup_slot_id':'MORNING','subtotal':100,'discount':10,'total':90,'payment_method':'UPI','items':[]})
    orders_repo.create_order({'customer_id':'C2','address_id':'A2','service_code':'STANDARD','pickup_slot_id':'EVENING','subtotal':200,'discount':0,'total':200,'payment_method':'COD','items':[]})
    rows=reports_service.generate('orders',{})
    revenue=reports_service.generate('revenue',{})[0]
    assert len(rows)==2
    assert revenue['order_count']==2
    assert revenue['net_revenue']==290
    assert revenue['discounts']==10
    assert revenue['cod_value']==200

def test_inventory_and_hanger_mis_reports():
    inventory_repo.create({'item_type':'BAG','item_code':'B1'})
    inventory_repo.create({'item_type':'BOX','item_code':'X1'})
    hangers_repo.create({'customer_id':'C1','quantity':3,'status':'ISSUED'})
    bags=reports_service.generate('bags_boxes',{})
    hangers=reports_service.generate('hangers',{})
    assert {x['item_type'] for x in bags}=={'BAG','BOX'}
    assert hangers[0]['quantity']==3
