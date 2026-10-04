from app.modules.payments import repository as repo
from app.integrations.payment import get_payment_provider
from app.modules.orders.service import get as get_order

def create(order_id, method):
    order=get_order(order_id)
    if not order: raise ValueError('Order not found')
    if method == 'COD': return repo.create_payment({'order_id':order_id,'method':method,'amount':order['total'],'currency':order['currency'],'provider':'none','status':'PENDING'})
    if method not in {'UPI','CARD'}: raise ValueError('Unsupported payment method')
    provider=get_payment_provider(); po=provider.create_order(order_id=order_id,amount=float(order['total']),currency=order['currency'],receipt=order_id)
    row=repo.create_payment({'order_id':order_id,'method':method,'amount':order['total'],'currency':order['currency'],'provider':po['provider'],'provider_order_id':po['provider_order_id']})
    row.update(provider_order=po); repo.event(row['payment_id'],'PAYMENT_ORDER_CREATED',po); return row

def verify(payment_id, data):
    row=repo.get(payment_id)
    if not row: raise ValueError('Payment not found')
    if row.get("provider_order_id") and data.get("provider_order_id") != row["provider_order_id"]:
        raise ValueError("Provider order mismatch")
    verified=get_payment_provider().verify(**data)
    if not verified['verified']: raise ValueError('Payment verification failed')
    updated=repo.update_payment(payment_id,'PAID',provider_payment_id=data['provider_payment_id'],provider_order_id=data['provider_order_id'])
    repo.event(payment_id,'PAYMENT_VERIFIED',verified); return updated

def get(payment_id): return repo.get(payment_id)
def list_for_order(order_id): return repo.list_for_order(order_id)

