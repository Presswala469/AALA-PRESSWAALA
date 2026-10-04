from fastapi import APIRouter, Depends
from app.core.constants import UserRole
from app.core.permissions import require_role
from app.modules.orders import repository as orders
from app.modules.inventory import repository as inventory
from app.modules.complaints import repository as complaints
from app.modules.hangers import repository as hangers
router=APIRouter()
_admin=Depends(require_role(UserRole.SUPER_ADMIN,UserRole.ADMIN,UserRole.STATION_MANAGER))
@router.get('/dashboard',dependencies=[_admin])
def dashboard():
    o=list(orders._orders.values()); i=inventory.list_all(); c=list(complaints._complaints.values()); h=list(hangers._hangers.values())
    pending_hangers=sum(int(x.get('quantity',0) or 0) for x in h if x.get('status')=='PENDING')
    return {'orders':{'total':len(o),'ready':sum(x.get('status')=='READY_FOR_DELIVERY' for x in o),'out_for_delivery':sum(x.get('status')=='OUT_FOR_DELIVERY' for x in o),'delivered':sum(x.get('status')=='DELIVERED' for x in o)},'complaints':{'total':len(c),'open':sum(x.get('status') not in {'CLOSED','REJECTED'} for x in c)},'inventory':{'total':len(i),'available':sum(x.get('status')=='AVAILABLE' for x in i)},'hanger_pending':pending_hangers,'hanger_red_alert':pending_hangers>30}
@router.get('/inventory/summary',dependencies=[_admin])
def inventory_summary():
    rows=inventory.list_all();out={}
    for r in rows:out[r['status']]=out.get(r['status'],0)+1
    return {'by_status':out,'total':len(rows)}
