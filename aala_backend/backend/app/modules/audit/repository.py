from copy import deepcopy
from datetime import datetime, timezone
from app.core.config import settings
from app.core.database import get_connection
_logs=[]
def now(): return datetime.now(timezone.utc).isoformat()
def record(data):
    row={**deepcopy(data),'created_at':now()}
    if not settings.database_url:_logs.append(row);return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into audit_logs(actor_user_id,action,entity_type,entity_id,old_values,new_values,ip_address,device_id) values(%s,%s,%s,%s,%s,%s,%s,%s)",(data.get('actor_user_id'),data['action'],data['entity_type'],data.get('entity_id'),data.get('old_values'),data.get('new_values'),data.get('ip_address'),data.get('device_id')));conn.commit()
    return row
def list_all(entity_type=None,limit=100):
    if not settings.database_url:
        rows=[x for x in _logs if not entity_type or x.get('entity_type')==entity_type];return deepcopy(rows[-limit:][::-1])
    with get_connection() as conn:
        with conn.cursor() as cur:
            if entity_type:cur.execute("select actor_user_id,action,entity_type,entity_id,old_values,new_values,ip_address,device_id,created_at from audit_logs where entity_type=%s order by created_at desc limit %s",(entity_type,limit))
            else:cur.execute("select actor_user_id,action,entity_type,entity_id,old_values,new_values,ip_address,device_id,created_at from audit_logs order by created_at desc limit %s",(limit,))
            rows=cur.fetchall()
    keys=['actor_user_id','action','entity_type','entity_id','old_values','new_values','ip_address','device_id','created_at'];return [dict(zip(keys,r)) for r in rows]

