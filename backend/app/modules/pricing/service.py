from decimal import Decimal, ROUND_HALF_UP
from app.modules.pricing.repository import get_price,set_price
from app.modules.services_catalog.repository import get_service
from app.modules.garments.repository import get_category

def money(v): return Decimal(v).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
def quote(service_code,items,station_code=None):
 service=get_service(service_code)
 if not service: raise ValueError('Service not found')
 out=[];subtotal=Decimal('0')
 for item in items:
  code=str(item['garment_code']).upper(); qty=int(item['quantity'])
  if qty<1: raise ValueError('Quantity must be at least 1')
  if not get_category(code): raise ValueError(f'Garment category not found: {code}')
  price=get_price(service_code,code,station_code)
  if price is None: raise ValueError(f'Price not configured: {service_code}/{code}')
  line=money(price*qty);subtotal+=line;out.append({'garment_code':code,'quantity':qty,'unit_price':money(price),'line_total':line})
 surcharge=Decimal('0')
 total=money(subtotal+surcharge)
 return {'service_code':service_code.upper(),'items':out,'subtotal':money(subtotal),'surcharge':money(surcharge),'total':total,'currency':'INR'}
def save_price(data): return set_price(data)

