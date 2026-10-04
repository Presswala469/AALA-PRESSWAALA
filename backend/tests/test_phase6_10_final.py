from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.modules.service_controls import repository as controls

client=TestClient(app)

def test_phase6c_routes_present():
    paths={r.path for r in app.routes}
    assert '/api/v1/service-controls/credits' in paths
    assert '/api/v1/service-controls/refunds' in paths

def test_phase7_admin_dashboard_route_present():
    assert any(r.path=='/api/v1/admin/dashboard' for r in app.routes)

def test_phase8_reports_catalog_complete():
    from app.modules.reports.schemas import aREPORT_TYPES
    required={'revenue','orders','customers','partners','stations','garments','hangers','bags_boxes','offers','complaints','customer_locations','customer_history'}
    assert required <= aREPORT_TYPES

def test_phase9_security_headers_and_request_id():
    r=client.get('/api/v1/health')
    assert r.status_code==200
    assert r.headers.get('X-Request-ID')
    assert r.headers.get('X-Content-Type-Options')=='nosniff'
    assert r.headers.get('X-Frame-Options')=='DENY'

def test_phase10_release_gate_shape():
    # Protected route must reject unauthenticated callers; implementation exists for production gate.
    r=client.get('/api/v1/release/readiness')
    assert r.status_code==401

def test_credit_repository_contract_without_db():
    old=settings.database_url
    settings.database_url=''
    row=controls.create_credit({'customer_id':'CUST-1','amount':125,'reason':'Service recovery'},'ADMIN-1')
    assert row['status']=='ISSUED' and row['amount']==125
    assert controls.list_credits('CUST-1')[0]['credit_id']==row['credit_id']
    settings.database_url=old
