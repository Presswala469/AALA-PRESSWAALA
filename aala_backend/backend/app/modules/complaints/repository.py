from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
from app.core.config import settings
from app.core.database import get_connection
_complaints={}; _events={}
def now(): return datetime.now(timezone.utc).isoformat()
def create(data):
    cid=f"CMP-{uuid4().hex[:10].upper()}"; row={**deepcopy(data),'complaint_id':cid,'status':'NEW','created_at':now()}
    if not settings.database_url: _complaints[cid]=row; _events[cid]=[]; return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into complaints(complaint_id,order_id,customer_id,category,description,status) values(%s,%s,%s,%s,%s,%s)",(cid,row['order_id'],row['customer_id'],row['category'],row['description'],'NEW')); conn.commit()
    return row
def get(cid): return deepcopy(_complaints.get(cid))
def update(cid,status,**values):
    row=_complaints.get(cid)
    if not row:return None
    row.update(values,status=status,updated_at=now()); _events.setdefault(cid,[]).append({'status':status,**deepcopy(values),'created_at':now()}); return deepcopy(row)
def events(cid): return deepcopy(_events.get(cid,[]))

