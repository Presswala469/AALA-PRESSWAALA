from secrets import randbelow
from app.modules.delivery import repository as repo
from app.modules.orders.service import get as get_order, change_status

def _order(order_id):
    o=get_order(order_id)
    if not o: raise ValueError('Order not found')
    return o

def assign(order_id, partner_id):
    o=_order(order_id)
    if o['status'] != 'READY_FOR_DELIVERY': raise ValueError('Order must be READY_FOR_DELIVERY before delivery assignment')
    return repo.create_job({'order_id':order_id,'partner_id':partner_id})

def start(order_id, partner_id):
    _order(order_id); job=repo.get_job(order_id)
    if not job or job['partner_id'] != partner_id: raise ValueError('Delivery partner is not assigned to this order')
    code=f'{randbelow(900000)+100000}'
    repo.save_code(order_id,code)
    changed=change_status(order_id,'OUT_FOR_DELIVERY',actor=f'partner:{partner_id}')
    return {'job':job,'delivery_code':repo.get_code(order_id),'order':changed}

def confirm(order_id, partner_id, data):
    o=_order(order_id); job=repo.get_job(order_id); code=repo.get_code(order_id)
    if o['status'] != 'OUT_FOR_DELIVERY': raise ValueError('Order must be OUT_FOR_DELIVERY before delivery confirmation')
    if not job or job['partner_id'] != partner_id: raise ValueError('Delivery partner is not assigned to this order')
    if not code or not code['active'] or data['delivery_code'] != code['delivery_code']: raise ValueError('Invalid or expired delivery code')
    changed=change_status(order_id,'DELIVERED',actor=f'partner:{partner_id}',reason=data.get('receiver_name'))
    repo.invalidate_code(order_id)
    return {'order':changed,'delivery_code':repo.get_code(order_id),'receiver_name':data.get('receiver_name')}

def exception(order_id, partner_id, data):
    o=_order(order_id); job=repo.get_job(order_id)
    if not job or job['partner_id'] != partner_id: raise ValueError('Delivery partner is not assigned to this order')
    if o['status'] not in {'OUT_FOR_DELIVERY','READY_FOR_DELIVERY'}: raise ValueError('Delivery exception is not allowed for current order status')
    return repo.save_exception(order_id,{'partner_id':partner_id,**data})

def get_job(order_id): return repo.get_job(order_id)
def get_code(order_id): return repo.get_code(order_id)

