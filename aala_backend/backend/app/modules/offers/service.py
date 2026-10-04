from decimal import Decimal, ROUND_HALF_UP
from app.modules.offers import repository as repo

def create(data): return repo.create(data)
def list_active(): return repo.list_active()
def apply(data):
    offer=repo.get_by_code(data['code'])
    if not offer: raise ValueError('Offer not found or disabled')
    subtotal=Decimal(str(data['subtotal']))
    if subtotal < Decimal(str(offer.get('min_order') or 0)): raise ValueError('Minimum order amount not met')
    for key in ('customer_type','city','station_code','area','building'):
        target=offer.get(key)
        if target and target.lower()!=str(data.get(key) or '').lower(): raise ValueError('Offer is not applicable to this customer/location')
    if offer['discount_type']=='PERCENT': discount=(subtotal*Decimal(str(offer['discount_value']))/Decimal('100')).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
    else: discount=Decimal(str(offer['discount_value']))
    if offer.get('max_discount') is not None: discount=min(discount,Decimal(str(offer['max_discount'])))
    discount=min(discount,subtotal)
    repo.record_usage({'offer_id':offer['offer_id'],'code':offer['code'],'subtotal':subtotal,'discount':discount})
    return {'offer_id':offer['offer_id'],'code':offer['code'],'discount':discount,'payable':subtotal-discount}

