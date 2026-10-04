from datetime import datetime,timezone
from app.modules.pickup.repository import list_slots,upsert
_jobs={}
def slots(station_code=None): return list_slots(station_code)
def save(data): return upsert(data)
def assign(order_id,partner_id):
    row={'order_id':order_id,'partner_id':partner_id,'assigned_at':datetime.now(timezone.utc).isoformat()}; _jobs[order_id]=row; return row
def job(order_id): return _jobs.get(order_id)

