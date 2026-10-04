from copy import deepcopy
from uuid import uuid4
from datetime import datetime,timezone
from app.core.config import settings
from app.core.database import get_connection
_zones={}; _assignments=[]
def now(): return datetime.now(timezone.utc).isoformat()
def create(data):
    row={**data,'id':str(uuid4()),'created_at':now(),'updated_at':now()}
    if not settings.database_url:_zones[row['zone_code']]=row;return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''insert into zones(zone_code,name,city,active) values(%s,%s,%s,%s) on conflict(zone_code) do update set name=excluded.name,city=excluded.city,active=excluded.active,updated_at=now() returning id,zone_code,name,city,active,created_at''',(data['zone_code'],data['name'],data.get('city'),data.get('active',True)));r=cur.fetchone();conn.commit()
    return dict(zip(('id','zone_code','name','city','active','created_at'),r))
def list_all():
    if not settings.database_url:return [deepcopy(x) for x in _zones.values() if x['active']]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select id,zone_code,name,city,active,created_at from zones where active=true order by name');rows=cur.fetchall()
    return [dict(zip(('id','zone_code','name','city','active','created_at'),r)) for r in rows]
def assign(data):
    if not settings.database_url:
        _assignments.append({**data,'assigned_at':now(),'active':data.get('active',True)});return deepcopy(_assignments[-1])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('insert into user_zone_assignments(user_id,zone_id,active) values(%s,%s,%s) on conflict do nothing returning id,user_id,zone_id,active,assigned_at',(data['user_id'],data['zone_id'],data.get('active',True)));r=cur.fetchone();conn.commit()
    if not r: raise ValueError('Active zone assignment already exists')
    return dict(zip(('id','user_id','zone_id','active','assigned_at'),r))
