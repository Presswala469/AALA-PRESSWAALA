from app.modules.audit import repository as repo
def record(data): return repo.record(data)
def list_all(entity_type=None,limit=100): return repo.list_all(entity_type,limit)

