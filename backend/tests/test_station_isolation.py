import pytest


def test_station_manager_cannot_access_unassigned_station(monkeypatch):
    from app.core import permissions
    permissions.enforce_station_access._dev_assignments = {('9999999999', 'ST01')}
    with pytest.raises(Exception):
        permissions.enforce_station_access('ST02', {'role': 'station_manager', 'sub': '9999999999'})


def test_station_manager_can_access_assigned_station(monkeypatch):
    from app.core import permissions
    permissions.enforce_station_access._dev_assignments = {('9999999999', 'ST01')}
    assert permissions.enforce_station_access('ST01', {'role': 'station_manager', 'sub': '9999999999'}) == 'ST01'


def test_partner_cannot_use_unassigned_station(monkeypatch):
    from app.core import permissions
    monkeypatch.setattr(permissions, 'current_partner_id', lambda claims: 'PAR-1')
    permissions.enforce_partner_station._dev_assignments = {('PAR-1', 'ST01')}
    with pytest.raises(Exception):
        permissions.enforce_partner_station('PAR-1', 'ST02', {'role': 'partner', 'sub': '9999999999'})


def test_partner_can_use_assigned_station(monkeypatch):
    from app.core import permissions
    monkeypatch.setattr(permissions, 'current_partner_id', lambda claims: 'PAR-1')
    permissions.enforce_partner_station._dev_assignments = {('PAR-1', 'ST01')}
    assert permissions.enforce_partner_station('PAR-1', 'ST01', {'role': 'partner', 'sub': '9999999999'}) == 'ST01'
