from app.modules.orders.service import get as get_order
from app.modules.ratings import repository as repo

def create(order_id, data):
    order=get_order(order_id)
    if not order: raise ValueError('Order not found')
    if order['status'] != 'DELIVERED': raise ValueError('Rating is available only after delivery')
    return repo.create(order_id,data)

def get(order_id): return repo.get(order_id)
