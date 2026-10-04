from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_public_company_config():
    r = client.get("/api/v1/company/public")
    assert r.status_code == 200
    assert r.json()["display_name"] == "AALA PRESSWAALA"

def test_otp_login():
    assert client.post("/api/v1/auth/otp/request", json={"mobile_number":"9876543210"}).status_code == 200
    r = client.post("/api/v1/auth/otp/verify", json={"mobile_number":"9876543210","otp":"123456"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"

def test_customer_global_number_is_permanent_sequence():
    a = client.post("/api/v1/customers", json={"mobile_number":"9876543210","full_name":"Test One"})
    b = client.post("/api/v1/customers", json={"mobile_number":"9876543211","full_name":"Test Two"})
    assert a.status_code == b.status_code == 200
    assert b.json()["global_customer_number"] == a.json()["global_customer_number"] + 1

def test_address_becomes_current():
    c = client.post("/api/v1/customers", json={"mobile_number":"9876543212","full_name":"Address User"})
    cid = c.json()["customer_id"]
    client.post("/api/v1/addresses", json={"customer_id":cid,"address_line":"One Street","city":"Lucknow","state":"UP","pincode":"226001"})
    client.post("/api/v1/addresses", json={"customer_id":cid,"address_line":"Two Street","city":"Lucknow","state":"UP","pincode":"226002"})
    rows = client.get(f"/api/v1/addresses/customer/{cid}").json()
    assert sum(1 for r in rows if r["is_current"]) == 1
