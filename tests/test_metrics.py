from fastapi.testclient import TestClient
import pytest

from src.main import app, record_broker_success_ratio, record_scheduler_tick

client = TestClient(app)


def test_health_endpoint():
    """Verify health endpoint returns HTTP 200 and expected status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_endpoint_response_format():
    """Verify /metrics endpoint returns HTTP 200 with Prometheus text format."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


def test_metrics_contains_required_metric_names():
    """Verify all four required metrics are exposed on the /metrics endpoint."""
    response = client.get("/metrics")
    body = response.text

    assert "requests_total" in body
    assert "latency_seconds" in body
    assert "broker_success_ratio" in body
    assert "scheduler_tick_duration" in body


def test_http_request_updates_requests_total_and_latency():
    """Verify hitting application endpoints updates HTTP request metrics."""
    # Issue request to populate middleware metrics
    client.get("/health")

    response = client.get("/metrics")
    body = response.text

    assert 'requests_total{endpoint="/health",http_status="200",method="GET"}' in body
    assert 'latency_seconds_count{endpoint="/health",method="GET"}' in body


def test_record_broker_success_ratio():
    """Verify broker success ratio gauge updates correctly."""
    record_broker_success_ratio(0.75)

    response = client.get("/metrics")
    body = response.text

    assert "broker_success_ratio 0.75" in body


def test_record_scheduler_tick_duration():
    """Verify scheduler tick duration histogram records observations."""
    record_scheduler_tick(0.15)

    response = client.get("/metrics")
    body = response.text

    assert "scheduler_tick_duration_count" in body
    assert "scheduler_tick_duration_sum" in body
