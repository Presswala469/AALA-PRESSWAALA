import pytest

def test_partner_station_db_query_contract_is_uuid_station_id_based(monkeypatch):
    from app.core import permissions
    monkeypatch.setattr(permissions, "current_partner_id", lambda claims: "PAR-1")
    permissions.enforce_partner_station._dev_assignments = {("PAR-1", "ST01")}
    assert permissions.enforce_partner_station(
        "PAR-1", "ST01", {"role": "partner", "sub": "9999999999"}
    ) == "ST01"

def test_partner_identity_resolver_rejects_mismatched_id(monkeypatch):
    from app.core import permissions
    monkeypatch.setattr(permissions, "current_partner_id", lambda claims: "PARTNER-A")
    with pytest.raises(Exception):
        permissions.enforce_partner_identity(
            "PARTNER-B",
            {"role": "partner", "sub": "9999999999"},
        )
