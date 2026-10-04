from app.modules.notifications import repository as repo
def queue(data): return repo.create(data)
def mark(nid,status):
    if status not in {'SENT','DELIVERED','FAILED','READ'}: raise ValueError('Invalid notification status')
    return repo.update(nid,status)
def list_for_recipient(recipient_id): return repo.for_recipient(recipient_id)

