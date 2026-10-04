import pytest
from decimal import Decimal
from app.modules.orders import repository as order_repo
from app.modules.delivery import service as delivery
from app.modules.payments import service as payments
from app.modules.invoices import service as invoices

@pytest.fixture(autouse=True)
def reset():
    order_repo._orders.clear(); order_repo._events.clear()
    import app.modules.delivery.repository as dr
    dr._jobs.clear(); dr._codes.clear(); dr._exceptions.clear()
    import app.modules.payments.repository as pr
    pr._payments.clear(); pr._events.clear()
    import app.modules.invoices.repository as ir
    ir._invoices.clear()

def make_order(status='READY_FOR_DELIVERY'):
    o=order_repo.create_order({'customer_id':'C1','address_id':'A1','service_code':'STANDARD','pickup_slot_id':'S1','items':[{'garment_code':'SHIRT','quantity':2,'unit_price':10,'line_total':20}], 'subtotal':20,'discount':0,'total':20,'currency':'INR','payment_method':'UPI','actor':'test'})
    order_repo._orders[o['order_id']]['status']=status
    return o

def test_delivery_assignment_and_start():
    o=make_order(); j=delivery.assign(o['order_id'],'P01'); r=delivery.start(o['order_id'],'P01')
    assert j['partner_id']=='P01' and r['order']['status']=='OUT_FOR_DELIVERY' and r['delivery_code']['active']

def test_delivery_code_is_invalidated_after_success():
    o=make_order(); delivery.assign(o['order_id'],'P01'); r=delivery.start(o['order_id'],'P01')
    done=delivery.confirm(o['order_id'],'P01',{'delivery_code':r['delivery_code']['delivery_code'],'receiver_name':'R'})
    assert done['order']['status']=='DELIVERED' and done['delivery_code']['active'] is False

def test_wrong_delivery_code_rejected():
    o=make_order(); delivery.assign(o['order_id'],'P01'); delivery.start(o['order_id'],'P01')
    with pytest.raises(ValueError,match='Invalid or expired delivery code'):
        delivery.confirm(o['order_id'],'P01',{'delivery_code':'000000'})

def test_payment_mock_order_and_verify():
    o=make_order(); p=payments.create(o['order_id'],'UPI')
    assert p['provider']=='mock' and p['provider_order_id']
    paid=payments.verify(p['payment_id'],{'provider_order_id':p['provider_order_id'],'provider_payment_id':'mock_pay_001','signature':'dev'})
    assert paid['status']=='PAID'

def test_cod_payment_boundary():
    o=make_order(); p=payments.create(o['order_id'],'COD')
    assert p['status']=='PENDING' and p['provider']=='none'

def test_invoice_snapshots_company_details():
    o=make_order(); inv=invoices.create(o['order_id'],Decimal('3'))
    assert inv['invoice_number'].startswith('APW-')
    assert inv['company_snapshot']['display_name']=='AALA PRESSWAALA'
    assert inv['total']==Decimal('23')
