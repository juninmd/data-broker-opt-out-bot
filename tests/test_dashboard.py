import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from src.db.database import (
    init_db,
    add_request,
    get_requests,
    update_broker_health,
    get_broker_health,
    create_otp_token,
    verify_and_use_otp_token,
    create_session,
    validate_session,
)
from src.dashboard.main import app

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["DATABASE_PATH"] = path
    init_db(path)
    yield path
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def client(temp_db):
    os.environ.pop("DISABLE_AUTH", None)
    with TestClient(app) as c:
        yield c

def test_db_operations(temp_db):
    # Test request operations
    req_id = add_request("DataBrokerA", "opt-out", "PENDING", "Initial request", db_path=temp_db)
    assert req_id > 0
    requests = get_requests(db_path=temp_db)
    assert len(requests) == 1
    assert requests[0]["broker_name"] == "DataBrokerA"
    assert requests[0]["status"] == "PENDING"

    # Test broker health operations
    update_broker_health("DataBrokerA", "HEALTHY", 120, db_path=temp_db)
    health = get_broker_health(db_path=temp_db)
    assert len(health) == 1
    assert health[0]["broker_name"] == "DataBrokerA"
    assert health[0]["status"] == "HEALTHY"
    assert health[0]["response_time_ms"] == 120

    # Test OTP token operations
    token = create_otp_token(expires_in_minutes=5, db_path=temp_db)
    assert verify_and_use_otp_token(token, db_path=temp_db) is True
    # Second use must fail (single use)
    assert verify_and_use_otp_token(token, db_path=temp_db) is False

    # Test session operations
    session_id = create_session(db_path=temp_db)
    assert validate_session(session_id, db_path=temp_db) is True
    assert validate_session("non-existent-session", db_path=temp_db) is False

def test_unauthenticated_access(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 401

    response = client.get("/dashboard/timeline", follow_redirects=False)
    assert response.status_code == 401

    response = client.get("/dashboard/broker-health", follow_redirects=False)
    assert response.status_code == 401

    response = client.get("/dashboard/export", follow_redirects=False)
    assert response.status_code == 401

def test_otp_login_flow(client, temp_db):
    token = create_otp_token(db_path=temp_db)

    # Login with valid token
    response = client.get(f"/auth/login?token={token}", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"
    assert "dashboard_session=" in response.headers.get("set-cookie", "")

    # Retrieve cookie and test protected dashboard access
    cookie_value = response.cookies.get("dashboard_session")

    dash_res = client.get("/dashboard", cookies={"dashboard_session": cookie_value})
    assert dash_res.status_code == 200
    assert "Data Broker Opt-Out Dashboard" in dash_res.text

    # Re-using the same OTP token must fail
    fail_res = client.get(f"/auth/login?token={token}", follow_redirects=False)
    assert fail_res.status_code == 400

def test_htmx_endpoints_and_export(client, temp_db):
    # Populate test data
    add_request("BrokerX", "opt-out", "COMPLETED", "Success", db_path=temp_db)
    update_broker_health("BrokerX", "HEALTHY", 85, db_path=temp_db)

    token = create_otp_token(db_path=temp_db)
    login_res = client.get(f"/auth/login?token={token}", follow_redirects=False)
    session_cookie = login_res.cookies.get("dashboard_session")

    cookies = {"dashboard_session": session_cookie}

    # Test HTMX timeline endpoint
    timeline_res = client.get("/dashboard/timeline", cookies=cookies)
    assert timeline_res.status_code == 200
    assert "BrokerX" in timeline_res.text
    assert "COMPLETED" in timeline_res.text

    # Test HTMX broker health endpoint
    health_res = client.get("/dashboard/broker-health", cookies=cookies)
    assert health_res.status_code == 200
    assert "BrokerX" in health_res.text
    assert "85 ms" in health_res.text

    # Test Export CSV endpoint
    export_res = client.get("/dashboard/export", cookies=cookies)
    assert export_res.status_code == 200
    assert export_res.headers["content-type"].startswith("text/csv")
    csv_content = export_res.text
    assert "=== REQUEST TIMELINE ===" in csv_content
    assert "=== BROKER HEALTH ===" in csv_content
    assert "BrokerX" in csv_content

def test_disable_auth_env_var(client, temp_db):
    os.environ["DISABLE_AUTH"] = "true"
    dash_res = client.get("/dashboard")
    assert dash_res.status_code == 200
    os.environ.pop("DISABLE_AUTH", None)
