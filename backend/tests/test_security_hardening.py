from fastapi.testclient import TestClient

from app.main import app
from app.modules.auth.service import _token

client = TestClient(app)


def test_station_endpoints_require_authentication():
    assert client.get("/api/v1/station/stations/ST-01/incoming").status_code == 401
    assert (
        client.post(
            "/api/v1/station/orders/O-1/receive?station_code=ST-01&partner_id=P-1",
            json={"partner_handover_quantity": 1, "station_received_quantity": 1},
        ).status_code
        == 401
    )
    assert (
        client.get("/api/v1/station/orders/O-1/history").status_code
        == 401
    )


def test_station_manager_role_is_accepted_for_station_reads():
    token = _token("station-manager-test", "station_manager", "test-session-security")
    auth_client = TestClient(app)
    auth_client.headers.update({"Authorization": f"Bearer {token}"})
    # In-memory test mode still enforces station isolation; seed the authenticated manager's assignment.
    from app.core.permissions import enforce_station_access
    enforce_station_access._dev_assignments = {("station-manager-test", "ST-01")}
    response = auth_client.get("/api/v1/station/stations/ST-01/incoming")
    assert response.status_code == 200
