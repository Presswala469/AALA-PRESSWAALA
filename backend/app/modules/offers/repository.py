from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
from app.core.config import settings
from app.core.database import get_connection
_offers={}; _usage=[]
def now(): return datetime.now(timezone.utc).isoformat()
def create(data):
    oid=f"OFF-{uuid4().hex[:10].upper()}"; row={**deepcopy(data),'offer_id':oid,'created_at':now()}
    if not settings.database_url: _offers[oid]=row; return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into offers(offer_id,code,name,discount_type,discount_value,start_at,end_at,days,min_order,max_discount,priority,enabled,customer_type,city,station_code,area,building) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", tuple(row.get(k) for k in ('offer_id','code','name','discount_type','discount_value','start_at','end_at','days','min_order','max_discount','priority','enabled','customer_type','city','station_code','area','building'))); conn.commit()
    return row
def list_active(at=None):
    if not settings.database_url: return sorted([deepcopy(x) for x in _offers.values() if x.get('enabled',True)],key=lambda x:x.get('priority',0),reverse=True)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select offer_id,code,name,discount_type,discount_value,start_at,end_at,days,min_order,max_discount,priority,enabled,customer_type,city,station_code,area,building from offers where enabled=true order by priority desc")
            rows=cur.fetchall()
    keys=('offer_id','code','name','discount_type','discount_value','start_at','end_at','days','min_order','max_discount','priority','enabled','customer_type','city','station_code','area','building')
    return [dict(zip(keys,r)) for r in rows]
def get_by_code(code): return next((deepcopy(x) for x in _offers.values() if x.get('code','').upper()==code.upper() and x.get('enabled',True)),None)
def record_usage(data): _usage.append({**deepcopy(data),'used_at':now()}); return deepcopy(_usage[-1])

