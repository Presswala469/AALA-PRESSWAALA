from app.modules.company.repository import get_company, update_company

def public_config():
    row = get_company()
    return {k: row.get(k) for k in ("legal_name","display_name","logo_url","registered_address","service_address","city","state","pincode","gstin","phone","email","website","support_phone","support_email","terms_url","privacy_url","refund_policy_url","cancellation_policy_url","currency","timezone")}

def save_company(values: dict, actor: str):
    old, new = update_company(values)
    return {"success": True, "actor": actor, "version": new["version"], "changed_fields": sorted(values.keys()), "company": public_config(), "audit": {"old_values": old, "new_values": new}}

