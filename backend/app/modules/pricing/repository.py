from decimal import Decimal
from app.core.config import settings
from app.core.database import get_connection
_default={
 ('STANDARD','SHIRT'):Decimal('15'),('STANDARD','TROUSER'):Decimal('20'),('STANDARD','T_SHIRT'):Decimal('10'),('STANDARD','HANDKERCHIEF'):Decimal('5'),
 ('OVERNIGHT_EXPRESS','SHIRT'):Decimal('25'),('OVERNIGHT_EXPRESS','TROUSER'):Decimal('30'),('OVERNIGHT_EXPRESS','T_SHIRT'):Decimal('20'),('OVERNIGHT_EXPRESS','HANDKERCHIEF'):Decimal('10'),
 ('TWO_HOUR_EXPRESS','SHIRT'):Decimal('35'),('TWO_HOUR_EXPRESS','TROUSER'):Decimal('40'),('TWO_HOUR_EXPRESS','T_SHIRT'):Decimal('30'),('TWO_HOUR_EXPRESS','HANDKERCHIEF'):Decimal('15'),
}
def get_price(service_code,garment_code,station_code=None):
 if not settings.database_url:return _default.get((service_code.upper(),garment_code.upper()))
 with get_connection() as conn:
  with conn.cursor() as cur:
   cur.execute("""select unit_price from garment_prices where service_code=%s and garment_code=%s
   and (station_code=%s or station_code is null) and active=true order by station_code nulls last limit 1""",(service_code.upper(),garment_code.upper(),station_code));r=cur.fetchone()
 return Decimal(str(r[0])) if r else None
def set_price(data):
 if not settings.database_url:
  _default[(data['service_code'].upper(),data['garment_code'].upper())]=Decimal(str(data['unit_price']));return {**data,'service_code':data['service_code'].upper(),'garment_code':data['garment_code'].upper()}
 with get_connection() as conn:
  with conn.cursor() as cur:
   cur.execute("""insert into garment_prices(service_code,garment_code,station_code,unit_price,min_quantity,express_surcharge)
   values(%s,%s,%s,%s,%s,%s) returning id""",(data['service_code'].upper(),data['garment_code'].upper(),data.get('station_code'),data['unit_price'],data.get('min_quantity',1),data.get('express_surcharge',0)));rid=cur.fetchone()[0];conn.commit()
 return {**data,'id':str(rid)}

