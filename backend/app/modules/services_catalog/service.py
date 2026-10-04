from app.modules.services_catalog.repository import list_services,get_service,upsert_service

def list_active(): return list_services()
def get(code): return get_service(code)
def save(data): return upsert_service(data)

