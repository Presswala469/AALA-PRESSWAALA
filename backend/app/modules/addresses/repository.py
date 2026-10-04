from uuid import uuid4
from app.core.database import get_connection
from app.core.config import settings

_addresses: dict[str, dict] = {}
_history: list[dict] = []

def add(data: dict) -> dict:
    if settings.database_url:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("select id,address_line,city,state,pincode,building_society,latitude,longitude from customer_addresses where customer_id=%s and is_current=true for update",(data['customer_id'],))
                previous=cur.fetchone()
                if previous:
                    snapshot={"address_id":str(previous[0]),"address_line":previous[1],"city":previous[2],"state":previous[3],"pincode":previous[4],"building_society":previous[5],"latitude":previous[6],"longitude":previous[7]}
                    cur.execute("update customer_addresses set is_current=false,updated_at=now() where id=%s",(previous[0],))
                    cur.execute("insert into customer_address_history(customer_id,source_address_id,address_snapshot) select customer_id,id,%s::jsonb from customer_addresses where id=%s",(str(snapshot).replace("'","\""),previous[0]))
                cur.execute("insert into customer_addresses(customer_id,label,address_line,city,state,pincode,building_society,latitude,longitude,is_current) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,true) returning id,created_at",(data['customer_id'],data.get('label','Home'),data['address_line'],data['city'],data['state'],data['pincode'],data.get('building_society'),data.get('latitude'),data.get('longitude')))
                row=cur.fetchone(); conn.commit()
                return {"address_id":str(row[0]),"is_current":True,**data}
    for row in _addresses.values():
        if row["customer_id"] == data["customer_id"] and row["is_current"]:
            row["is_current"] = False; _history.append(dict(row))
    row = {"address_id": str(uuid4()), "is_current": True, **data}; _addresses[row["address_id"]] = row; return row

def list_for_customer(customer_id: str):
    if settings.database_url:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("select id,label,address_line,city,state,pincode,building_society,latitude,longitude,is_current from customer_addresses where customer_id=(select id from customers where customer_id=%s) order by created_at desc",(customer_id,)); rows=cur.fetchall()
        return [{"address_id":str(r[0]),"label":r[1],"address_line":r[2],"city":r[3],"state":r[4],"pincode":r[5],"building_society":r[6],"latitude":r[7],"longitude":r[8],"is_current":r[9]} for r in rows]
    return [row for row in _addresses.values() if row["customer_id"] == customer_id]

