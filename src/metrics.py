from prometheus_client import Counter, Gauge, Histogram, REGISTRY, generate_latest, CONTENT_TYPE_LATEST

# Prometheus metrics definition
REQUESTS_TOTAL = Counter(
    "requests_total",
    "Total number of HTTP requests processed",
    ["method", "endpoint", "http_status"],
)

LATENCY_SECONDS = Histogram(
    "latency_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

BROKER_SUCCESS_RATIO = Gauge(
    "broker_success_ratio",
    "Current success ratio of data broker opt-out requests",
)

SCHEDULER_TICK_DURATION = Histogram(
    "scheduler_tick_duration",
    "Duration of background scheduler execution ticks in seconds",
)


def get_metrics_response() -> tuple[bytes, str]:
    """Generates Prometheus format metrics output and its content-type header."""
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
