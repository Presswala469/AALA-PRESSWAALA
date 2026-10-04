from uuid import uuid4
from app.core.database import get_connection
from app.core.config import settings

_customers: dict[str, dict] = {}
_next_global = 1

def create_customer(data: dict) -> dict:
    global _next_global
    if settings.database_url:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cid=f"CUS-{uuid4().hex[:10].upper()}"
                cur.execute("select id from users where mobile_number=%s",(data['mobile_number'],))
                user=cur.fetchone()
                cur.execute("insert into customers(customer_id,user_id,name,mobile_number,email,alternate_mobile,photo_url) values(%s,%s,%s,%s,%s,%s,%s) returning customer_id,global_customer_number,status",(cid,user[0] if user else None,data['name'],data['mobile_number'],data.get('email'),data.get('alternate_mobile'),data.get('photo_url')))
                row=cur.fetchone(); conn.commit()
                return {"customer_id":row[0],"global_customer_number":row[1],"is_active":row[2]=='active',**data}
    customer_id = f"CUS-{uuid4().hex[:10].upper()}"
    row = {"customer_id": customer_id, "global_customer_number": _next_global, "is_active": True, **data}
    _next_global += 1; _customers[customer_id] = row; return row

def get_customer(customer_id: str):
    if settings.database_url:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("select customer_id,global_customer_number,name,mobile_number,email,alternate_mobile,photo_url,status from customers where customer_id=%s",(customer_id,)); row=cur.fetchone()
        if not row: return None
        return {"customer_id":row[0],"global_customer_number":row[1],"name":row[2],"mobile_number":row[3],"email":row[4],"alternate_mobile":row[5],"photo_url":row[6],"is_active":row[7]=='active'}
    return _customers.get(customer_id)

