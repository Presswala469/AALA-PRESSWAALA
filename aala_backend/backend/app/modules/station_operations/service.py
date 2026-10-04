from app.modules.station_operations import repository as repo
from app.modules.orders.service import get as get_order, change_status

STATION_STATUSES = {'RECEIVED','READY_FOR_DELIVERY','ON_HOLD','REJECTED'}

def _require_order(order_id):
    order=get_order(order_id)
    if not order: raise ValueError('Order not found')
    return order

def arrival(order_id, station_code, partner_id, data):
    _require_order(order_id)
    return repo.save_arrival(order_id,{**data,'order_id':order_id,'partner_id':partner_id,'station_code':station_code,'arrived_at':data.get('arrived_at') or repo.now()})

def receive(order_id, station_code, partner_id, data):
    order=_require_order(order_id)
    if order['status'] != 'IRON_STATION': raise ValueError(f"Order must be in IRON_STATION before receiving; current status is {order['status']}")
    discrepancy=data['station_received_quantity'] != data['partner_handover_quantity']
    if discrepancy and not (data.get('reason') or '').strip(): raise ValueError('Reason is required for quantity discrepancy')
    row=repo.save_receipt(order_id,{**data,'order_id':order_id,'partner_id':partner_id,'station_code':station_code,'discrepancy':discrepancy,'received_at':repo.now()})
    changed=change_status(order_id,'RECEIVED',actor=f'station:{station_code}',reason=data.get('reason'))
    repo.save_status(order_id,{'order_id':order_id,'station_code':station_code,'status':'RECEIVED','reason':data.get('reason'),'remarks':data.get('remarks'),'actor':f'station:{station_code}','updated_at':repo.now()})
    return {**row,'order':changed}

def status(order_id, station_code, data):
    order=_require_order(order_id); new=data['status'].upper()
    if new not in STATION_STATUSES: raise ValueError('Invalid station status')
    if new == 'RECEIVED': raise ValueError('Use the receive endpoint to record quantities')
    changed=change_status(order_id,new,actor=f'station:{station_code}',reason=data.get('reason'))
    if not changed: raise ValueError('Order not found')
    row=repo.save_status(order_id,{**data,'order_id':order_id,'station_code':station_code,'status':new,'actor':f'station:{station_code}','updated_at':repo.now()})
    return {**row,'order':changed}

def evidence(order_id, station_code, actor, data):
    _require_order(order_id)
    return repo.save_evidence(order_id,{**data,'order_id':order_id,'station_code':station_code,'actor':actor,'created_at':repo.now()})

def receipt(order_id): return repo.get(repo._receipts,order_id)
def history(order_id): return repo.list_history(order_id)
def incoming(station_code): return repo.list_incoming(station_code,['IRON_STATION','RECEIVED','ON_HOLD'])

