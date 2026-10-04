from fastapi import APIRouter, Depends, HTTPException, Response

from app.core.constants import UserRole
from app.core.permissions import current_claims, require_role
from app.modules.invoices.schemas import InvoiceCreate
from app.modules.invoices import service

router = APIRouter()


def err(exc: ValueError) -> None:
    raise HTTPException(400, str(exc))


_AUTH = Depends(current_claims)
_ADMIN = Depends(require_role(UserRole.SUPER_ADMIN, UserRole.ADMIN))


@router.post("/orders/{order_id}", response_model=dict, dependencies=[_ADMIN])
def create(order_id: str, payload: InvoiceCreate):
    try:
        return service.create(order_id, payload.tax_amount)
    except ValueError as exc:
        err(exc)


@router.get("/{invoice_id}", response_model=dict, dependencies=[_AUTH])
def get(invoice_id: str):
    return service.get(invoice_id) or {}


@router.get("/orders/{order_id}", response_model=list, dependencies=[_AUTH])
def by_order(order_id: str):
    return service.by_order(order_id)


@router.get("/{invoice_id}/pdf", response_class=Response, dependencies=[_AUTH])
def pdf(invoice_id: str):
    try:
        data = service.pdf(invoice_id)
        return Response(
            content=data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="{invoice_id}.pdf"'},
        )
    except ValueError as exc:
        raise HTTPException(404, str(exc))
