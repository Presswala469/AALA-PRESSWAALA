import pytest
from app.modules.delivery import service as delivery_service
from app.modules.delivery import repository as delivery_repo


def test_partner_identity_mismatch_rejected(monkeypatch):
    from app.core import permissions
    monkeypatch.setattr(permissions, 'current_partner_id', lambda claims: 'PAR-1')
    with pytest.raises(Exception):
        permissions.enforce_partner_identity('PAR-OTHER', {'role':'partner', 'sub':'9999999999'})


def test_delivery_view_rejects_unassigned_partner(monkeypatch):
    monkeypatch.setattr(delivery_repo, 'get_job', lambda order_id: {'order_id': order_id, 'partner_id':'PAR-1'})
    monkeypatch.setattr('app.core.permissions.current_partner_id', lambda claims: 'PAR-2')
    with pytest.raises(ValueError, match='Delivery access denied'):
        delivery_service.authorize_view('ORD-1', {'role':'partner','sub':'x'})
