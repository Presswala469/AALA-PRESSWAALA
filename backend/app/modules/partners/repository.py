from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
from app.core.config import settings
from app.core.database import get_connection
_partners={}; _assignments={}; _arrivals={}; _verifications={}; _damage={}; _bags={}; _pickups={}
def _pid(): return f"PAR-{uuid4().hex[:8].upper()}"
def create_partner(data):
    pid=_pid(); row={**data,'partner_id':pid,'created_at':datetime.now(timezone.utc).isoformat()}
    if not settings.database_url: _partners[pid]=row; return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into partners(partner_id,employee_id,name,mobile_number,active) values(%s,%s,%s,%s,%s) returning created_at",(pid,data['employee_id'],data['name'],data['mobile_number'],data['active']))
            row['created_at']=cur.fetchone()[0].isoformat(); conn.commit()
    _partners[pid]=row; return deepcopy(row)
def list_partners(station_code=None):
    if not settings.database_url: return [deepcopy(x) for x in _partners.values() if not station_code or _assignments.get(x['partner_id'],{}).get('station_code')==station_code]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select p.partner_id,p.employee_id,p.name,p.mobile_number,p.active,a.station_code from partners p left join partner_station_assignments a on a.partner_id=p.partner_id and a.active=true where (%s is null or a.station_code=%s) order by p.name",(station_code,station_code)); rows=cur.fetchall()
    return [dict(zip(('partner_id','employee_id','name','mobile_number','active','station_code'),r)) for r in rows]
def assign(pid,station):
    row={'partner_id':pid,'station_code':station,'assigned_at':datetime.now(timezone.utc).isoformat(),'active':True}; _assignments[pid]=row
    if settings.database_url:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("update partner_station_assignments set active=false,ended_at=now() where partner_id=%s and active=true",(pid,))
                cur.execute("insert into partner_station_assignments(partner_id,station_code,active) values(%s,%s,true)",(pid,station)); conn.commit()
    return deepcopy(row)
def assignment(pid):
    if not settings.database_url:return deepcopy(_assignments.get(pid))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select partner_id,station_code,assigned_at,active from partner_station_assignments where partner_id=%s and active=true order by assigned_at desc limit 1",(pid,)); r=cur.fetchone()
    return dict(zip(('partner_id','station_code','assigned_at','active'),r)) if r else None
def record(key,store,data): store[key]=deepcopy(data); return deepcopy(data)
def get_store(store,key): return deepcopy(store.get(key))

