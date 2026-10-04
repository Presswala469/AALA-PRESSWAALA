from decimal import Decimal
import pytest
from app.modules.orders import repository as order_repo
from app.modules.invoices import repository as invoice_repo
from app.modules.invoices import service as invoice_service
from app.modules.payments import repository as payment_repo


@pytest.fixture(autouse=True)
def reset():
    order_repo._orders.clear(); order_repo._events.clear()
    invoice_repo._invoices.clear(); invoice_repo._items.clear(); invoice_repo._audits.clear()
    payment_repo._payments.clear(); payment_repo._events.clear()


def make_order():
    return order_repo.create_order({
        'customer_id':'C1','address_id':'A1','service_code':'STANDARD','pickup_slot_id':'S1',
        'items':[
            {'garment_code':'SHIRT','quantity':2,'unit_price':50,'line_total':100},
            {'garment_code':'PANT','quantity':1,'unit_price':100,'line_total':100},
        ],
        'subtotal':200,'discount':20,'total':180,'currency':'INR','payment_method':'UPI','actor':'test'
    })


def test_invoice_gst_breakup_and_snapshots():
    o = make_order()
    result = invoice_service.create(o['order_id'], tax_rate=Decimal('18'), tax_type='GST', tax_mode='INTRA')
    assert result['tax_amount'] == Decimal('32.40')
    assert result['cgst_amount'] == Decimal('16.20')
    assert result['sgst_amount'] == Decimal('16.20')
    assert result['igst_amount'] == Decimal('0')
    assert result['total'] == Decimal('212.40')
    assert result['customer_snapshot']['customer_id'] == 'C1'
    assert result['order_snapshot']['order_id'] == o['order_id']
    assert len(result['items']) == 2
    assert sum((Decimal(str(x['taxable_amount'])) for x in result['items']), Decimal('0')) == Decimal('180.00')
    assert sum((Decimal(str(x['tax_amount'])) for x in result['items']), Decimal('0')) == Decimal('32.40')
    assert result['audit_events'][0]['action'] == 'INVOICE_CREATED'


def test_interstate_igst():
    o = make_order()
    result = invoice_service.create(o['order_id'], tax_rate=Decimal('18'), tax_type='GST', tax_mode='INTER')
    assert result['cgst_amount'] == Decimal('0')
    assert result['sgst_amount'] == Decimal('0')
    assert result['igst_amount'] == Decimal('32.40')


def test_payment_reference_is_snapshotted():
    o = make_order()
    payment_repo.create_payment({
        'order_id':o['order_id'],'method':'UPI','amount':Decimal('180'),'currency':'INR',
        'provider':'mock','provider_order_id':'rzp_order_1','provider_payment_id':'pay_123','status':'PAID'
    })
    result = invoice_service.create(o['order_id'])
    assert result['payment_reference'] == 'pay_123'


def test_duplicate_active_invoice_is_rejected():
    o = make_order()
    invoice_service.create(o['order_id'])
    with pytest.raises(ValueError, match='Active invoice already exists'):
        invoice_service.create(o['order_id'])
