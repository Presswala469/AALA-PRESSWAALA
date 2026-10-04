from datetime import datetime, timezone
from app.modules.partners import repository as repo
def create(data): return repo.create_partner(data)
def list_all(station_code=None): return repo.list_partners(station_code)
def assign(partner_id,station_code):
    if not repo._partners.get(partner_id) and not repo.assignment(partner_id): raise ValueError('Partner not found')
    return repo.assign(partner_id,station_code)
def assignment(partner_id): return repo.assignment(partner_id)
def arrival(order_id,partner_id,data):
    data={**data,'order_id':order_id,'partner_id':partner_id,'arrived_at':data.get('arrived_at') or datetime.now(timezone.utc).isoformat()}; return repo.record(order_id,repo._arrivals,data)
def verify(order_id,partner_id,data):
    data={**data,'order_id':order_id,'partner_id':partner_id}; return repo.record(order_id,repo._verifications,data)
def damage(order_id,partner_id,data):
    data={**data,'order_id':order_id,'partner_id':partner_id,'recorded_at':datetime.now(timezone.utc).isoformat()}; key=f"{order_id}:{data['item_ref']}"; return repo.record(key,repo._damage,data)
def bag(order_id,partner_id,data):
    data={**data,'order_id':order_id,'partner_id':partner_id,'assigned_at':datetime.now(timezone.utc).isoformat()}; return repo.record(order_id,repo._bags,data)
def complete(order_id,partner_id,data):
    data={**data,'order_id':order_id,'partner_id':partner_id,'completed_at':datetime.now(timezone.utc).isoformat()}; return repo.record(order_id,repo._pickups,data)

def _order_transition(order_id, new_status, actor, reason=None):
    from app.modules.orders.service import change_status
    return change_status(order_id, new_status, actor=actor, reason=reason)

def mark_pickup_started(order_id, partner_id):
    return _order_transition(order_id, 'PICKUP', f'partner:{partner_id}')

def mark_station_handover(order_id, partner_id, reason=None):
    return _order_transition(order_id, 'IRON_STATION', f'partner:{partner_id}', reason)

