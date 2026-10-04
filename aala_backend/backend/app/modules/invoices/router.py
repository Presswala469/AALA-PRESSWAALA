from fastapi import APIRouter, Depends, HTTPException, Response
from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from app.modules.invoices.schemas import InvoiceCreate
from app.modules.invoices import service

router = APIRouter()


def _visible(invoice, claims):
    if not invoice:
        return False
    role = claims.get('role')
    if role in {UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value, UserRole.STATION_MANAGER.value}:
        return True
    return role == UserRole.CUSTOMER.value and str((invoice.get('customer_snapshot') or {}).get('customer_id')) == str(claims.get('sub'))


@router.post('/orders/{order_id}', response_model=dict, dependencies=[Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))])
def create(order_id, payload: InvoiceCreate):
    try:
        return service.create(order_id, tax_type=payload.tax_type, tax_mode=payload.tax_mode, payment_reference=payload.payment_reference, tax_rate=payload.tax_rate)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get('/{invoice_id}', response_model=dict)
def get(invoice_id, claims=Depends(current_claims)):
    invoice = service.get(invoice_id)
    if not invoice:
        raise HTTPException(404, 'Invoice not found')
    if not _visible(invoice, claims):
        raise HTTPException(403, 'Permission denied')
    return invoice


@router.get('/orders/{order_id}', response_model=list)
def by_order(order_id, claims=Depends(current_claims)):
    invoices = service.by_order(order_id)
    visible = [invoice for invoice in invoices if _visible(invoice, claims)]
    if not visible:
        raise HTTPException(403, 'Permission denied')
    return visible


@router.get('/{invoice_id}/pdf', response_class=Response)
def pdf(invoice_id, claims=Depends(current_claims)):
    invoice = service.get(invoice_id)
    if not invoice:
        raise HTTPException(404, 'Invoice not found')
    if not _visible(invoice, claims):
        raise HTTPException(403, 'Permission denied')
    try:
        data = service.pdf(invoice_id)
        return Response(content=data, media_type='application/pdf', headers={'Content-Disposition': f'inline; filename="{invoice_id}.pdf"'})
    except ValueError as e:
        raise HTTPException(404, str(e))
