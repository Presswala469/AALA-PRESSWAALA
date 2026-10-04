from copy import deepcopy
from app.core.config import settings
from app.core.database import get_connection
_default=[
 {"code":"SHIRT","name":"Shirt","small_garment":False,"active":True,"display_order":1},
 {"code":"TROUSER","name":"Trouser","small_garment":False,"active":True,"display_order":2},
 {"code":"T_SHIRT","name":"T-Shirt","small_garment":True,"active":True,"display_order":3},
 {"code":"HANDKERCHIEF","name":"Handkerchief","small_garment":True,"active":True,"display_order":4},
]
_items={x['code']:x for x in _default}
def list_categories():
 if not settings.database_url:return sorted((deepcopy(x) for x in _items.values() if x['active']),key=lambda x:x['display_order'])
 with get_connection() as conn:
  with conn.cursor() as cur:
   cur.execute("select code,name,small_garment,active,display_order from garment_categories where active=true order by display_order,name")
   return [dict(zip(('code','name','small_garment','active','display_order'),r)) for r in cur.fetchall()]
def get_category(code):
 code=code.upper()
 if not settings.database_url:return deepcopy(_items.get(code))
 with get_connection() as conn:
  with conn.cursor() as cur:
   cur.execute("select code,name,small_garment,active,display_order from garment_categories where code=%s and active=true",(code,));r=cur.fetchone()
 return dict(zip(('code','name','small_garment','active','display_order'),r)) if r else None
def upsert_category(data):
 code=data['code'].upper()
 if not settings.database_url:
  _items[code]={**data,'code':code,'active':True};return deepcopy(_items[code])
 with get_connection() as conn:
  with conn.cursor() as cur:
   cur.execute("""insert into garment_categories(code,name,small_garment,display_order) values(%s,%s,%s,%s)
   on conflict(code) do update set name=excluded.name,small_garment=excluded.small_garment,display_order=excluded.display_order,updated_at=now()
   returning code,name,small_garment,active,display_order""",(code,data['name'],data.get('small_garment',False),data.get('display_order',0)));r=cur.fetchone();conn.commit()
 return dict(zip(('code','name','small_garment','active','display_order'),r))

