from app.modules.hangers import repository as repo
def create(data): return repo.create(data)
def update(hid,data,actor=None):
    if data['status'] not in {'ISSUED','RETURNED','PENDING'}: raise ValueError('Invalid hanger status')
    return repo.update(hid,data['status'],actor,data.get('remarks'))
def get(hid): return repo.get(hid)
def customer(customer_id): return repo.for_customer(customer_id)
def request_return(data): return repo.create_return(data)
def returns(customer_id): return repo.returns(customer_id)

