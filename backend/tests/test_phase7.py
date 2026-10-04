import pytest
from app.modules.inventory import service as inventory_service, repository as inventory_repo
from app.modules.audit import service as audit_service, repository as audit_repo

@pytest.fixture(autouse=True)
def reset():
    inventory_repo._items.clear(); inventory_repo._movements.clear(); audit_repo._logs.clear()

def test_inventory_lifecycle_and_history():
    item=inventory_service.create({'item_type':'BAG','item_code':'BAG-001','location':'HQ'})
    assert item['status']=='AVAILABLE'
    updated=inventory_service.update(item['inventory_id'], {'status':'ISSUED','holder_type':'PARTNER','holder_id':'P-1'}, actor='admin:1')
    assert updated['status']=='ISSUED'
    history=inventory_service.history(item['inventory_id'])
    assert len(history)>=2

def test_inventory_exception_requires_remarks():
    item=inventory_service.create({'item_type':'BOX'})
    with pytest.raises(ValueError, match='Remarks'):
        inventory_service.update(item['inventory_id'], {'status':'LOST'})
    updated=inventory_service.update(item['inventory_id'], {'status':'LOST','remarks':'Not returned by partner'}, actor='admin:1')
    assert updated['status']=='LOST'

def test_audit_record_and_filter():
    audit_service.record({'action':'UPDATE','entity_type':'COMPANY','entity_id':'1','old_values':{'name':'A'},'new_values':{'name':'B'}})
    audit_service.record({'action':'CREATE','entity_type':'ORDER','entity_id':'2'})
    logs=audit_service.list_all('COMPANY')
    assert len(logs)==1 and logs[0]['entity_type']=='COMPANY'
