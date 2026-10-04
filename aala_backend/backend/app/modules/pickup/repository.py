from copy import deepcopy
from app.core.config import settings
from app.core.database import get_connection
_slots={
 'MORNING':{'slot_id':'MORNING','label':'Morning','start_time':'09:00','end_time':'12:00','station_code':None,'max_orders':20,'active':True},
 'AFTERNOON':{'slot_id':'AFTERNOON','label':'Afternoon','start_time':'12:00','end_time':'16:00','station_code':None,'max_orders':20,'active':True},
 'EVENING':{'slot_id':'EVENING','label':'Evening','start_time':'16:00','end_time':'20:00','station_code':None,'max_orders':20,'active':True},
}
def list_slots(station_code=None):
 if not settings.database_url:return [deepcopy(x) for x in _slots.values() if x['active'] and (not station_code or x['station_code'] in (None,station_code))]
 with get_connection() as conn:
  with conn.cursor() as cur:
   cur.execute("select slot_id,label,start_time::text,end_time::text,station_code,max_orders,active from pickup_slots where active=true and (station_code=%s or station_code is null) order by start_time",(station_code,));rows=cur.fetchall()
 return [dict(zip(('slot_id','label','start_time','end_time','station_code','max_orders','active'),r)) for r in rows]
def upsert(data):
 if not settings.database_url:_slots[data['slot_id']]=deepcopy(data);return deepcopy(data)
 with get_connection() as conn:
  with conn.cursor() as cur:
   cur.execute("""insert into pickup_slots(slot_id,label,start_time,end_time,station_code,max_orders,active) values(%s,%s,%s,%s,%s,%s,%s)
   on conflict(slot_id) do update set label=excluded.label,start_time=excluded.start_time,end_time=excluded.end_time,station_code=excluded.station_code,max_orders=excluded.max_orders,active=excluded.active,updated_at=now()""",tuple(data.values()));conn.commit()
 return data

