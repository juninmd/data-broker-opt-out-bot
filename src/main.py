import time
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse

from src.metrics import (
    BROKER_SUCCESS_RATIO,
    LATENCY_SECONDS,
    REQUESTS_TOTAL,
    SCHEDULER_TICK_DURATION,
    get_metrics_response,
)

app = FastAPI(
    title="Data Broker Opt-Out Bot",
    description="Autonomous Telegram bot tracking opt-out requests with Prometheus observability",
    version="1.0.0",
)


@app.middleware("http")
async def prometheus_metrics_middleware(request: Request, call_next):
    """Middleware to track requests_total counter and latency_seconds histogram."""
    if request.url.path == "/metrics":
        return await call_next(request)

    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time

    route = request.scope.get("route")
    endpoint = route.path if route else request.url.path
    method = request.method
    status_code = str(response.status_code)

    LATENCY_SECONDS.labels(method=method, endpoint=endpoint).observe(duration)
    REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, http_status=status_code).inc()

    return response


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Exposes Prometheus metrics endpoint."""
    content, content_type = get_metrics_response()
    return Response(content=content, media_type=content_type)


@app.get("/health")
async def health():
    """Service health check endpoint."""
    return {"status": "ok"}


def record_broker_success_ratio(ratio: float) -> None:
    """Updates the current broker success ratio gauge."""
    BROKER_SUCCESS_RATIO.set(ratio)


def record_scheduler_tick(duration_seconds: float) -> None:
    """Records duration of a scheduler tick."""
    SCHEDULER_TICK_DURATION.observe(duration_seconds)
