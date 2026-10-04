from datetime import datetime, timezone
from app.modules.hangers import repository as repo

def _alert(row):
    if not row or row.get('status') != 'PENDING':
        return row
    raw=row.get('pending_since') or row.get('updated_at') or row.get('created_at')
    try:
        dt=raw if isinstance(raw,datetime) else datetime.fromisoformat(str(raw).replace('Z','+00:00'))
        age=(datetime.now(timezone.utc)-dt).total_seconds()/86400
        row['pending_days']=round(max(age,0),2)
        row['alert_level']='RED' if age>30 else 'NORMAL'
    except Exception:
        row['pending_days']=None; row['alert_level']='NORMAL'
    return row

def create(data): return repo.create(data)
def update(hid,data,actor=None):
    if data['status'] not in {'ISSUED','RETURNED','PENDING'}: raise ValueError('Invalid hanger status')
    row=repo.update(hid,data['status'],actor,data.get('remarks'))
    return _alert(row) if row else None
def get(hid): return _alert(repo.get(hid))
def customer(customer_id): return [_alert(x) for x in repo.for_customer(customer_id)]
def request_return(data): return repo.create_return(data)
def returns(customer_id): return repo.returns(customer_id)
