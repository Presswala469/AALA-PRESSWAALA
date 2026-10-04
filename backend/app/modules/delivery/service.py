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
    stored=repo.get_code(order_id)
    return {'job':job,'delivery_code':{'order_id':order_id,'delivery_code':code,'active':stored['active'] if stored else True,'expires_at':stored.get('expires_at') if stored else None},'order':changed}

def confirm(order_id, partner_id, data):
    o=_order(order_id); job=repo.get_job(order_id)
    if o['status'] != 'OUT_FOR_DELIVERY': raise ValueError('Order must be OUT_FOR_DELIVERY before delivery confirmation')
    if not job or job['partner_id'] != partner_id: raise ValueError('Delivery partner is not assigned to this order')
    if not repo.code_matches(order_id,data['delivery_code']): raise ValueError('Invalid or expired delivery code')
    repo.save_event(order_id,{'partner_id':partner_id,'delivery_mode':'STANDARD','receiver_name':data['receiver_name'],'receiver_mobile':data.get('receiver_mobile'),'latitude':data.get('latitude'),'longitude':data.get('longitude'),'remarks':data.get('remarks')})
    changed=change_status(order_id,'DELIVERED',actor=f'partner:{partner_id}',reason=data.get('receiver_name'))
    repo.invalidate_code(order_id)
    return {'order':changed,'delivery_code':repo.get_code(order_id),'receiver_name':data.get('receiver_name')}

def exception(order_id, partner_id, data):
    o=_order(order_id); job=repo.get_job(order_id)
    if not job or job['partner_id'] != partner_id: raise ValueError('Delivery partner is not assigned to this order')
    if o['status'] not in {'OUT_FOR_DELIVERY','READY_FOR_DELIVERY'}: raise ValueError('Delivery exception is not allowed for current order status')
    row=repo.save_event(order_id,{'partner_id':partner_id,'delivery_mode':'MANUAL','reason':data['reason'],'receiver_name':data['receiver_name'],'receiver_mobile':data['receiver_mobile'],'evidence_url':data['evidence_url'],'house_number':data.get('house_number'),'latitude':data.get('latitude'),'longitude':data.get('longitude'),'remarks':data.get('remarks')})
    changed=change_status(order_id,'DELIVERED',actor=f'partner:{partner_id}',reason=f"MANUAL: {data['reason']}")
    return {'event':row,'order':changed}

def authorize_view(order_id, claims):
    if claims.get('role') != 'partner':
        return True
    from app.core.permissions import current_partner_id
    partner_id = current_partner_id(claims)
    job = repo.get_job(order_id)
    if not job or job.get('partner_id') != partner_id:
        raise ValueError('Delivery access denied')
    return True

def get_job(order_id): return repo.get_job(order_id)
def get_code(order_id):
    row=repo.get_code(order_id)
    if not row:return None
    return {k:v for k,v in row.items() if k not in {'delivery_code_hash'}}
