from copy import deepcopy
from app.core.database import get_connection

_company = {
    "legal_name": "AALA PRESSWAALA", "display_name": "AALA PRESSWAALA", "logo_url": None,
    "registered_address": None, "service_address": None, "city": None, "state": None, "pincode": None,
    "gstin": None, "pan": None, "cin": None, "phone": None, "email": None, "website": None,
    "support_phone": None, "support_email": None, "invoice_prefix": "APW", "invoice_terms": None,
    "invoice_footer": None, "currency": "INR", "timezone": "Asia/Kolkata", "terms_url": None,
    "privacy_url": None, "refund_policy_url": None, "cancellation_policy_url": None, "version": 1,
}

def get_company() -> dict:
    if not __import__('app.core.config', fromlist=['settings']).settings.database_url:
        return deepcopy(_company)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select legal_name,display_name,logo_url,registered_address,service_address,city,state,pincode,gstin,pan,cin,phone,email,website,support_phone,support_email,invoice_prefix,invoice_terms,invoice_footer,currency,timezone,terms_url,privacy_url,refund_policy_url,cancellation_policy_url,version from company_profiles where is_active=true order by created_at limit 1")
            row = cur.fetchone()
    if not row:
        return deepcopy(_company)
    keys = list(_company.keys())
    return dict(zip(keys, row))

def update_company(values: dict) -> tuple[dict, dict]:
    old = get_company()
    if not __import__('app.core.config', fromlist=['settings']).settings.database_url:
        _company.update(values); _company['version'] += 1; return old, deepcopy(_company)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("select id,version from company_profiles where is_active=true order by created_at limit 1")
            row = cur.fetchone()
            if not row:
                fields = {**_company, **values}
                cols = ','.join(fields.keys()); placeholders=','.join(['%s']*len(fields))
                cur.execute(f"insert into company_profiles ({cols}) values ({placeholders}) returning id", tuple(fields.values()))
            else:
                company_id, version = row
                values = {**values, 'version': version+1}
                sets=','.join(f"{k}=%s" for k in values)
                cur.execute(f"update company_profiles set {sets},updated_at=now() where id=%s", (*values.values(),company_id))
            conn.commit()
    return old, get_company()

