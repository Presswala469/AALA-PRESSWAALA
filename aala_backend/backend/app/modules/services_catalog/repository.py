from copy import deepcopy
from app.core.config import settings
from app.core.database import get_connection

_default = [
    {"code":"STANDARD","name":"Standard","description":"Standard ironing service","service_type":"standard","active":True,"display_order":1},
    {"code":"OVERNIGHT_EXPRESS","name":"Overnight Express","description":"Priority overnight service","service_type":"overnight_express","active":True,"display_order":2},
    {"code":"TWO_HOUR_EXPRESS","name":"2-hour Express","description":"Priority two-hour service","service_type":"two_hour_express","active":True,"display_order":3},
]
_services = {x["code"]: x for x in _default}

def list_services():
    if not settings.database_url:
        return sorted((deepcopy(x) for x in _services.values() if x["active"]), key=lambda x:x["display_order"])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select code,name,description,service_type,active,display_order from services where active=true order by display_order,name")
            return [dict(zip(("code","name","description","service_type","active","display_order"), r)) for r in cur.fetchall()]

def get_service(code):
    if not settings.database_url:
        return deepcopy(_services.get(code.upper()))
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select code,name,description,service_type,active,display_order from services where code=%s and active=true",(code.upper(),))
            r=cur.fetchone()
    return dict(zip(("code","name","description","service_type","active","display_order"),r)) if r else None

def upsert_service(data):
    code=data["code"].upper()
    if not settings.database_url:
        _services[code]={**data,"code":code,"active":True}
        return deepcopy(_services[code])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""insert into services(code,name,description,service_type,display_order) values(%s,%s,%s,%s,%s)
            on conflict(code) do update set name=excluded.name,description=excluded.description,service_type=excluded.service_type,display_order=excluded.display_order,updated_at=now()
            returning code,name,description,service_type,active,display_order""",(code,data["name"],data.get("description"),data.get("service_type","standard"),data.get("display_order",0)))
            r=cur.fetchone(); conn.commit()
    return dict(zip(("code","name","description","service_type","active","display_order"),r))

