from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
from app.core.config import settings
from app.core.database import get_connection

_requests={}
def now(): return datetime.now(timezone.utc).isoformat()

def create(data, actor_user_id=None):
    rid=f'SUP-{uuid4().hex[:10].upper()}'
    row={**deepcopy(data),'request_id':rid,'status':'OPEN','created_by':actor_user_id,'created_at':now()}
    if not settings.database_url:
        _requests[rid]=row; return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''insert into station_support_requests(request_id,station_code,order_id,request_type,description,priority,status,created_by)
                           values(%s,%s,%s,%s,%s,%s,%s,%s) returning created_at''',
                        (rid,data['station_code'],data.get('order_id'),data['request_type'],data['description'],data.get('priority','NORMAL'),'OPEN',actor_user_id))
            row['created_at']=cur.fetchone()[0].isoformat(); conn.commit()
    return row

def update(rid,status,actor_user_id=None):
    if not settings.database_url:
        if rid not in _requests: return None
        _requests[rid].update(status=status,resolved_by=actor_user_id if status in {'RESOLVED','CLOSED'} else None,resolved_at=now() if status in {'RESOLVED','CLOSED'} else None,updated_at=now())
        return deepcopy(_requests[rid])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''update station_support_requests set status=%s, resolved_by=case when %s in ('RESOLVED','CLOSED') then %s else resolved_by end,
                           resolved_at=case when %s in ('RESOLVED','CLOSED') then now() else resolved_at end, updated_at=now()
                           where request_id=%s''',(status,status,actor_user_id,status,rid))
            if cur.rowcount==0: conn.rollback(); return None
            cur.execute('select request_id,station_code,order_id,request_type,description,priority,status,created_by,resolved_by,resolved_at,created_at,updated_at from station_support_requests where request_id=%s',(rid,)); r=cur.fetchone(); conn.commit()
    keys=('request_id','station_code','order_id','request_type','description','priority','status','created_by','resolved_by','resolved_at','created_at','updated_at')
    return dict(zip(keys,r))

def list_for_station(station_code):
    if not settings.database_url:return [deepcopy(x) for x in _requests.values() if x['station_code']==station_code]
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('select request_id,station_code,order_id,request_type,description,priority,status,created_by,resolved_by,resolved_at,created_at,updated_at from station_support_requests where station_code=%s order by created_at desc',(station_code,)); rows=cur.fetchall()
    keys=('request_id','station_code','order_id','request_type','description','priority','status','created_by','resolved_by','resolved_at','created_at','updated_at')
    return [dict(zip(keys,r)) for r in rows]
