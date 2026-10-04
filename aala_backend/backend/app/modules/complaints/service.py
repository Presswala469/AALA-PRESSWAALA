from datetime import datetime, timezone, timedelta
from app.modules.complaints import repository as repo
from app.modules.orders.service import get as get_order
_ALLOWED={'NEW','ASSIGNED','UNDER_INVESTIGATION','ACTION_REQUIRED','RESOLVED','CLOSED','REJECTED'}
def create(data):
    order=get_order(data['order_id'])
    if not order: raise ValueError('Order not found')
    if order['status']!='DELIVERED': raise ValueError('Complaint is available only after delivery')
    delivered=None
    for e in reversed(__import__('app.modules.orders.service',fromlist=['history']).history(data['order_id'])):
        if e.get('to_status')=='DELIVERED': delivered=e.get('created_at'); break
    if delivered:
        dt=datetime.fromisoformat(delivered.replace('Z','+00:00'))
        if datetime.now(timezone.utc)-dt>timedelta(hours=24): raise ValueError('Complaint window of 24 hours has expired')
    return repo.create(data)
def update(cid,data):
    if data['status'] not in _ALLOWED or data['status']=='NEW': raise ValueError('Invalid complaint status')
    if not repo.get(cid): raise ValueError('Complaint not found')
    return repo.update(cid,data['status'],remarks=data.get('remarks'),assigned_to=data.get('assigned_to'))
def get(cid): return repo.get(cid)
def events(cid): return repo.events(cid)

