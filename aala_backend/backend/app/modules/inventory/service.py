from app.modules.inventory import repository as repo

def create(data, actor='system'): return repo.create(data)
def list_all(status=None,item_type=None): return repo.list_all(status,item_type)
def update(iid, data, actor='system'):
    if data.get('status') in {'LOST','DAMAGED','UNDER_REPAIR','REPLACEMENT'} and not data.get('remarks'):
        raise ValueError('Remarks are mandatory for exception inventory status')
    return repo.update(iid,data,actor)
def adjust(iid, data, actor='system'):
    item=repo.get(iid)
    if not item: raise ValueError('Inventory item not found')
    event=repo.record_movement(iid,data['action'],actor,item,item,data.get('remarks'),data.get('evidence_url'))
    return event
def history(iid): return repo.movements(iid)

