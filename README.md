# data-broker-opt-out-bot

An autonomous Telegram bot that submits and tracks opt-out requests to major Brazilian and US data brokers, using a combination of public APIs and headless-browser scraping backed by recorded HTML fixtures.

## Observability & Prometheus Metrics

The application exposes a `/metrics` endpoint for Prometheus scraping.

### Metrics Exposed

- `requests_total`: Counter tracking total HTTP requests processed (labeled by `method`, `endpoint`, and `http_status`).
- `latency_seconds`: Histogram tracking HTTP request duration in seconds (labeled by `method` and `endpoint`).
- `broker_success_ratio`: Gauge representing the current success ratio of data broker opt-out operations.
- `scheduler_tick_duration`: Histogram tracking the execution duration of scheduler background ticks in seconds.

### Prometheus Configuration & Alerts

Prometheus scrape configuration and alert rules are located under `prometheus/`:

- `prometheus/prometheus.yml`: Configures Prometheus to scrape `/metrics` every 5 seconds.
- `prometheus/alerts.yml`: Defines alert rules, including `BrokerSuccessRatioLow` which triggers when `broker_success_ratio < 0.5`.

### Grafana Dashboard

A pre-configured Grafana dashboard JSON is committed in `grafana/dashboard.json`.
It includes visual panels for:
1. Total HTTP Requests (`requests_total`)
2. Request Latency (`latency_seconds`)
3. Data Broker Success Ratio (`broker_success_ratio`) with threshold highlights (Red < 0.5, Yellow 0.5-0.8, Green > 0.8)
4. Scheduler Tick Duration (`scheduler_tick_duration`)

To import: Open Grafana -> Dashboards -> Import -> Upload `grafana/dashboard.json`.

## Quickstart & Testing

Install dependencies:
```bash
pip install -r requirements.txt
```

Run unit tests:
```bash
pytest
```

Run application server:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```
