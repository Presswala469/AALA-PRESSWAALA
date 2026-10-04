from app.modules.garments.repository import list_categories,get_category,upsert_category
def list_active(): return list_categories()
def get(code): return get_category(code)
def save(data): return upsert_category(data)

