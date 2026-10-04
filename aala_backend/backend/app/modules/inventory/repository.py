from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
from app.core.config import settings
from app.core.database import get_connection

_items={}; _movements=[]
def now(): return datetime.now(timezone.utc).isoformat()

def create(data):
    iid=data.get('inventory_id') or f"INV-{uuid4().hex[:10].upper()}"
    row={**deepcopy(data),'inventory_id':iid,'status':'AVAILABLE','created_at':now()}
    if not settings.database_url:
        _items[iid]=row; _movements.append({'inventory_id':iid,'action':'CREATED','created_at':now()}); return deepcopy(row)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into bags_boxes(inventory_id,item_type,item_code,status,holder_type,holder_id,location,remarks) values(%s,%s,%s,%s,%s,%s,%s,%s)", (iid,row['item_type'],row.get('item_code'),row['status'],row.get('holder_type'),row.get('holder_id'),row.get('location'),row.get('remarks'))); conn.commit()
    return row

def get(iid):
    if not settings.database_url: return deepcopy(_items.get(iid))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select inventory_id,item_type,item_code,status,holder_type,holder_id,location,remarks,created_at from bags_boxes where inventory_id=%s",(iid,)); r=cur.fetchone()
    if not r:return None
    keys=['inventory_id','item_type','item_code','status','holder_type','holder_id','location','remarks','created_at']; return dict(zip(keys,r))

def list_all(status=None,item_type=None):
    if not settings.database_url:
        rows=list(_items.values())
        if status: rows=[x for x in rows if x['status']==status]
        if item_type: rows=[x for x in rows if x['item_type']==item_type]
        return deepcopy(rows)
    with get_connection() as conn:
        with conn.cursor() as cur:
            q="select inventory_id,item_type,item_code,status,holder_type,holder_id,location,remarks,created_at from bags_boxes where 1=1"; p=[]
            if status:q+=" and status=%s";p.append(status)
            if item_type:q+=" and item_type=%s";p.append(item_type)
            q+=" order by created_at desc";cur.execute(q,p); rows=cur.fetchall()
    keys=['inventory_id','item_type','item_code','status','holder_type','holder_id','location','remarks','created_at'];return [dict(zip(keys,r)) for r in rows]

def update(iid, values, actor=None):
    old=get(iid)
    if not old:return None
    if not settings.database_url:
        _items[iid].update(values,updated_at=now()); new=deepcopy(_items[iid]); _movements.append({'inventory_id':iid,'action':'STATUS_CHANGED','actor':actor,'old':old,'new':new,'created_at':now()}); return new
    with get_connection() as conn:
        with conn.cursor() as cur:
            sets=','.join(f"{k}=%s" for k in values);cur.execute(f"update bags_boxes set {sets},updated_at=now() where inventory_id=%s",(*values.values(),iid));conn.commit()
    new=get(iid); record_movement(iid,'UPDATED',actor,old,new); return new

def record_movement(iid, action, actor, old=None, new=None, remarks=None, evidence_url=None):
    event={'inventory_id':iid,'action':action,'actor':actor,'old':deepcopy(old),'new':deepcopy(new),'remarks':remarks,'evidence_url':evidence_url,'created_at':now()}
    if not settings.database_url: _movements.append(event); return deepcopy(event)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("insert into inventory_movements(inventory_id,action,actor,old_values,new_values,remarks,evidence_url) values(%s,%s,%s,%s,%s,%s,%s)",(iid,action,actor,old,new,remarks,evidence_url));conn.commit()
    return event

def movements(iid):
    if not settings.database_url:return [deepcopy(x) for x in _movements if x['inventory_id']==iid]
    with get_connection() as conn:
        with conn.cursor() as cur:cur.execute("select action,actor,old_values,new_values,remarks,evidence_url,created_at from inventory_movements where inventory_id=%s order by created_at",(iid,));rows=cur.fetchall()
    return [{'action':r[0],'actor':r[1],'old':r[2],'new':r[3],'remarks':r[4],'evidence_url':r[5],'created_at':r[6]} for r in rows]

